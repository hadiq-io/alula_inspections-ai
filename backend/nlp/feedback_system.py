"""
User Feedback Validation System
================================
Human-in-the-loop learning system that allows users to validate 
AI responses as correct or incorrect, building a verified query library.

Features:
- User validation of AI responses (correct/incorrect)
- Clarification input for incorrect responses
- Bilingual support (English/Arabic)
- Integration with existing query_learning.py
- Faster promotion for user-validated queries
- Validated query library for future use

Author: AlUla Inspection AI
Version: 1.0
"""

import os
import json
import uuid
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class ValidationStatus(str, Enum):
    """Status of user validation."""
    PENDING = "pending"      # Awaiting user feedback
    CORRECT = "correct"      # User confirmed correct
    INCORRECT = "incorrect"  # User marked incorrect
    CLARIFIED = "clarified"  # User provided clarification
    RETRIED = "retried"      # Retried after clarification


@dataclass
class ValidatedQuery:
    """A user-validated query with feedback data."""
    message_id: str                    # Unique ID for this response
    conversation_id: Optional[str]     # Conversation context
    
    # Original request
    original_question: str
    original_question_lang: str        # 'en' or 'ar'
    
    # AI Response
    template_id: Optional[str]
    sql_query: str
    response_en: str
    response_ar: str
    chart_type: str = "bar"
    data_preview: str = ""             # JSON string of first few rows
    
    # Validation
    validation_status: str = ValidationStatus.PENDING
    validated_at: Optional[str] = None
    
    # Clarification (if incorrect)
    clarification_text: Optional[str] = None
    clarification_lang: Optional[str] = None
    expected_result: Optional[str] = None  # What user expected
    
    # Retry tracking
    retry_count: int = 0
    retry_message_ids: List[str] = field(default_factory=list)
    final_correct_response: Optional[str] = None
    
    # Learning integration
    promoted_to_learning: bool = False
    learning_query_id: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ValidatedQuery':
        # Handle retry_message_ids as JSON
        if isinstance(data.get('retry_message_ids'), str):
            data['retry_message_ids'] = json.loads(data['retry_message_ids'] or '[]')
        return cls(**data)


class FeedbackSystem:
    """
    User feedback and validation system.
    
    Workflow:
    1. AI generates response → create ValidatedQuery with PENDING status
    2. User clicks ✓ Correct → mark as CORRECT, promote to learning
    3. User clicks ✗ Wrong → mark as INCORRECT, request clarification
    4. User provides clarification → retry query
    5. Successful retry → mark original as CLARIFIED, new as CORRECT
    
    Storage: SQLite database for validated queries
    """
    
    # Bilingual labels
    LABELS = {
        'correct': {'en': 'Correct', 'ar': 'صحيح'},
        'incorrect': {'en': 'Wrong', 'ar': 'خطأ'},
        'clarify_prompt': {
            'en': 'Please describe what you expected:',
            'ar': 'يرجى وصف ما كنت تتوقعه:'
        },
        'thanks_correct': {
            'en': 'Thank you! This query has been saved for future use.',
            'ar': 'شكراً! تم حفظ هذا الاستعلام للاستخدام المستقبلي.'
        },
        'thanks_clarify': {
            'en': 'Thank you for the clarification. Let me try again.',
            'ar': 'شكراً للتوضيح. دعني أحاول مرة أخرى.'
        },
        'validation_recorded': {
            'en': 'Feedback recorded',
            'ar': 'تم تسجيل الملاحظات'
        }
    }
    
    def __init__(self, db_path: str = None):
        """
        Initialize the feedback system.
        
        Args:
            db_path: Path to SQLite database
        """
        self._lock = threading.Lock()
        
        # Default path in backend folder
        if db_path is None:
            backend_dir = Path(__file__).parent.parent
            db_path = str(backend_dir / "validated_queries.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for validated queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validated_queries (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT,
                original_question TEXT NOT NULL,
                original_question_lang TEXT DEFAULT 'en',
                template_id TEXT,
                sql_query TEXT,
                response_en TEXT,
                response_ar TEXT,
                chart_type TEXT DEFAULT 'bar',
                data_preview TEXT,
                validation_status TEXT DEFAULT 'pending',
                validated_at TEXT,
                clarification_text TEXT,
                clarification_lang TEXT,
                expected_result TEXT,
                retry_count INTEGER DEFAULT 0,
                retry_message_ids TEXT DEFAULT '[]',
                final_correct_response TEXT,
                promoted_to_learning INTEGER DEFAULT 0,
                learning_query_id TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Index for status lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_status 
            ON validated_queries(validation_status)
        """)
        
        # Index for question pattern matching
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_question 
            ON validated_queries(original_question)
        """)
        
        # Index for promoted queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promoted 
            ON validated_queries(promoted_to_learning)
        """)
        
        conn.commit()
        conn.close()
    
    def generate_message_id(self) -> str:
        """Generate a unique message ID."""
        return str(uuid.uuid4())
    
    def create_pending_validation(
        self,
        message_id: str,
        question: str,
        question_lang: str,
        sql_query: str,
        response_en: str,
        response_ar: str,
        template_id: str = None,
        chart_type: str = "bar",
        data_preview: Any = None,
        conversation_id: str = None
    ) -> ValidatedQuery:
        """
        Create a pending validation entry for an AI response.
        
        This should be called after every AI response to enable feedback.
        
        Args:
            message_id: Unique ID for this message
            question: Original user question
            question_lang: Language of question ('en' or 'ar')
            sql_query: Generated SQL
            response_en: English response text
            response_ar: Arabic response text
            template_id: SQL template used (if any)
            chart_type: Chart type suggested
            data_preview: First few rows of data (will be JSON serialized)
            conversation_id: Conversation context ID
            
        Returns:
            ValidatedQuery object
        """
        # Serialize data preview
        if data_preview is not None:
            if isinstance(data_preview, list) and len(data_preview) > 5:
                data_preview = data_preview[:5]  # Keep only first 5 rows
            data_preview_str = json.dumps(data_preview, default=str, ensure_ascii=False)
        else:
            data_preview_str = ""
        
        validated_query = ValidatedQuery(
            message_id=message_id,
            conversation_id=conversation_id,
            original_question=question,
            original_question_lang=question_lang,
            template_id=template_id,
            sql_query=sql_query,
            response_en=response_en,
            response_ar=response_ar,
            chart_type=chart_type,
            data_preview=data_preview_str,
            validation_status=ValidationStatus.PENDING
        )
        
        self._save_query(validated_query)
        return validated_query
    
    def validate_correct(
        self,
        message_id: str,
        learning_system: Any = None  # QueryLearningSystem
    ) -> Dict[str, Any]:
        """
        Mark a response as correct and promote to learning system.
        
        Args:
            message_id: The message ID to validate
            learning_system: Optional QueryLearningSystem for promotion
            
        Returns:
            Dict with status and bilingual feedback message
        """
        with self._lock:
            query = self._get_query(message_id)
            
            if not query:
                return {
                    'success': False,
                    'error': 'Message not found',
                    'message_en': 'Response not found',
                    'message_ar': 'الاستجابة غير موجودة'
                }
            
            # Update validation status
            query.validation_status = ValidationStatus.CORRECT
            query.validated_at = datetime.now().isoformat()
            query.updated_at = datetime.now().isoformat()
            
            # Promote to learning system if provided
            if learning_system and query.sql_query:
                try:
                    learned = learning_system.capture_query(
                        question=query.original_question,
                        sql=query.sql_query,
                        explanation_en=query.response_en,
                        explanation_ar=query.response_ar,
                        chart_type=query.chart_type,
                        success=True,
                        user_validated=True  # New flag for user-validated queries
                    )
                    query.promoted_to_learning = True
                    query.learning_query_id = learned.id
                except Exception as e:
                    print(f"[FeedbackSystem] Error promoting to learning: {e}")
            
            self._save_query(query)
            
            return {
                'success': True,
                'validation_status': ValidationStatus.CORRECT,
                'promoted': query.promoted_to_learning,
                'message_en': self.LABELS['thanks_correct']['en'],
                'message_ar': self.LABELS['thanks_correct']['ar']
            }
    
    def validate_incorrect(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Mark a response as incorrect and request clarification.
        
        Args:
            message_id: The message ID to mark as incorrect
            
        Returns:
            Dict with clarification prompt in both languages
        """
        with self._lock:
            query = self._get_query(message_id)
            
            if not query:
                return {
                    'success': False,
                    'error': 'Message not found',
                    'message_en': 'Response not found',
                    'message_ar': 'الاستجابة غير موجودة'
                }
            
            # Update validation status
            query.validation_status = ValidationStatus.INCORRECT
            query.validated_at = datetime.now().isoformat()
            query.updated_at = datetime.now().isoformat()
            
            self._save_query(query)
            
            return {
                'success': True,
                'validation_status': ValidationStatus.INCORRECT,
                'needs_clarification': True,
                'prompt_en': self.LABELS['clarify_prompt']['en'],
                'prompt_ar': self.LABELS['clarify_prompt']['ar'],
                'message_id': message_id
            }
    
    def submit_clarification(
        self,
        message_id: str,
        clarification: str,
        clarification_lang: str = 'en',
        expected_result: str = None
    ) -> Dict[str, Any]:
        """
        Submit user clarification for an incorrect response.
        
        Args:
            message_id: The original message ID
            clarification: User's clarification text
            clarification_lang: Language of clarification
            expected_result: What the user expected (optional)
            
        Returns:
            Dict with acknowledgment and retry context
        """
        with self._lock:
            query = self._get_query(message_id)
            
            if not query:
                return {
                    'success': False,
                    'error': 'Message not found'
                }
            
            # Store clarification
            query.clarification_text = clarification
            query.clarification_lang = clarification_lang
            query.expected_result = expected_result
            query.validation_status = ValidationStatus.CLARIFIED
            query.retry_count += 1
            query.updated_at = datetime.now().isoformat()
            
            self._save_query(query)
            
            return {
                'success': True,
                'validation_status': ValidationStatus.CLARIFIED,
                'original_question': query.original_question,
                'clarification': clarification,
                'retry_context': {
                    'original_message_id': message_id,
                    'retry_count': query.retry_count,
                    'clarification': clarification,
                    'expected': expected_result
                },
                'message_en': self.LABELS['thanks_clarify']['en'],
                'message_ar': self.LABELS['thanks_clarify']['ar']
            }
    
    def link_retry_response(
        self,
        original_message_id: str,
        new_message_id: str
    ) -> bool:
        """
        Link a retry response to the original message.
        
        Args:
            original_message_id: The original message that was clarified
            new_message_id: The new retry message ID
            
        Returns:
            Success status
        """
        with self._lock:
            query = self._get_query(original_message_id)
            
            if not query:
                return False
            
            query.retry_message_ids.append(new_message_id)
            query.validation_status = ValidationStatus.RETRIED
            query.updated_at = datetime.now().isoformat()
            
            self._save_query(query)
            return True
    
    def get_validated_for_question(
        self,
        question: str,
        limit: int = 5
    ) -> List[ValidatedQuery]:
        """
        Find validated (correct) queries similar to the given question.
        
        This can be used to pre-populate responses for similar questions.
        
        Args:
            question: Question to search for
            limit: Maximum results to return
            
        Returns:
            List of validated queries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search for similar validated queries
        # Using LIKE for basic pattern matching
        search_pattern = f"%{question[:50]}%"  # First 50 chars
        
        cursor.execute("""
            SELECT * FROM validated_queries
            WHERE validation_status = 'correct'
            AND promoted_to_learning = 1
            AND original_question LIKE ?
            ORDER BY validated_at DESC
            LIMIT ?
        """, (search_pattern, limit))
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            data['promoted_to_learning'] = bool(data['promoted_to_learning'])
            data['retry_message_ids'] = json.loads(data['retry_message_ids'] or '[]')
            results.append(ValidatedQuery.from_dict(data))
        
        conn.close()
        return results
    
    def get_validation_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current validation status for a message.
        
        Args:
            message_id: The message ID to check
            
        Returns:
            Dict with validation status or None
        """
        query = self._get_query(message_id)
        
        if not query:
            return None
        
        return {
            'message_id': message_id,
            'validation_status': query.validation_status,
            'validated_at': query.validated_at,
            'promoted': query.promoted_to_learning,
            'retry_count': query.retry_count
        }
    
    def get_pending_validations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent pending validations.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of pending validation summaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT message_id, original_question, created_at, template_id
            FROM validated_queries
            WHERE validation_status = 'pending'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'message_id': row[0],
                'question': row[1],
                'created_at': row[2],
                'template_id': row[3]
            })
        
        conn.close()
        return results
    
    def _get_query(self, message_id: str) -> Optional[ValidatedQuery]:
        """Get a validated query by message ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM validated_queries WHERE message_id = ?",
            (message_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        columns = [
            'message_id', 'conversation_id', 'original_question',
            'original_question_lang', 'template_id', 'sql_query',
            'response_en', 'response_ar', 'chart_type', 'data_preview',
            'validation_status', 'validated_at', 'clarification_text',
            'clarification_lang', 'expected_result', 'retry_count',
            'retry_message_ids', 'final_correct_response',
            'promoted_to_learning', 'learning_query_id',
            'created_at', 'updated_at'
        ]
        
        data = dict(zip(columns, row))
        data['promoted_to_learning'] = bool(data['promoted_to_learning'])
        data['retry_message_ids'] = json.loads(data['retry_message_ids'] or '[]')
        
        return ValidatedQuery.from_dict(data)
    
    def _save_query(self, query: ValidatedQuery) -> None:
        """Save or update a validated query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize retry_message_ids as JSON
        retry_ids_json = json.dumps(query.retry_message_ids)
        
        cursor.execute("""
            INSERT OR REPLACE INTO validated_queries (
                message_id, conversation_id, original_question,
                original_question_lang, template_id, sql_query,
                response_en, response_ar, chart_type, data_preview,
                validation_status, validated_at, clarification_text,
                clarification_lang, expected_result, retry_count,
                retry_message_ids, final_correct_response,
                promoted_to_learning, learning_query_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query.message_id, query.conversation_id, query.original_question,
            query.original_question_lang, query.template_id, query.sql_query,
            query.response_en, query.response_ar, query.chart_type, query.data_preview,
            query.validation_status, query.validated_at, query.clarification_text,
            query.clarification_lang, query.expected_result, query.retry_count,
            retry_ids_json, query.final_correct_response,
            1 if query.promoted_to_learning else 0, query.learning_query_id,
            query.created_at, query.updated_at
        ))
        
        conn.commit()
        conn.close()


# Singleton instance
_feedback_system: Optional[FeedbackSystem] = None


def get_feedback_system() -> FeedbackSystem:
    """Get or create the global feedback system instance."""
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem()
    return _feedback_system
