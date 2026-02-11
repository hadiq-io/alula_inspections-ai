"""
Correction Learner Module
=========================
Learns from user feedback to improve query understanding and response accuracy.
When users mark responses as incorrect and provide clarifications, this module
captures the patterns and generates improved SQL/responses for future queries.
"""

import json
import logging
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class CorrectionType(Enum):
    """Types of corrections users can make"""
    WRONG_DATA = "wrong_data"           # SQL returned wrong data
    WRONG_INTERPRETATION = "wrong_interpretation"  # Misunderstood the question
    MISSING_FILTERS = "missing_filters"  # Needed additional WHERE clauses
    WRONG_COLUMNS = "wrong_columns"      # Selected wrong columns
    WRONG_AGGREGATION = "wrong_aggregation"  # Wrong GROUP BY or SUM/AVG
    WRONG_TIME_RANGE = "wrong_time_range"  # Wrong date filter
    WRONG_ENTITY = "wrong_entity"        # Confused entities (location vs neighborhood)
    FORMATTING_ISSUE = "formatting"      # Output format was wrong
    OTHER = "other"


class ConfidenceLevel(Enum):
    """Confidence levels for learned corrections"""
    LOW = "low"           # 1 user confirmed
    MEDIUM = "medium"     # 2-4 users confirmed
    HIGH = "high"         # 5+ users confirmed or manually verified


@dataclass
class Correction:
    """A learned correction from user feedback"""
    id: str
    original_question: str
    original_sql: str
    clarification: str
    corrected_sql: Optional[str]
    correction_type: CorrectionType
    entity_mappings: Dict[str, str]  # e.g., {"location": "Al-Ula Old Town"}
    filter_additions: List[str]      # Additional WHERE clauses
    column_changes: Dict[str, str]   # Original -> Corrected column
    pattern_signature: str           # Hash for quick matching
    confidence: ConfidenceLevel
    confirmation_count: int
    created_at: datetime
    last_used: Optional[datetime] = None
    success_rate: float = 0.0


@dataclass
class ErrorPattern:
    """Pattern for tracking common errors"""
    pattern_id: str
    keywords: List[str]
    error_description: str
    suggested_fix: str
    occurrence_count: int
    examples: List[Dict[str, str]]
    resolution_sql_template: Optional[str] = None


class CorrectionLearner:
    """
    Main class for learning from user corrections and improving query accuracy.
    
    Features:
    - Captures user clarifications when responses are marked incorrect
    - Identifies patterns in misunderstood queries
    - Generates improved SQL based on learned corrections
    - Tracks error patterns to prevent recurring mistakes
    - Supports both SQLite (persistent) and in-memory storage
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the correction learner.
        
        Args:
            db_path: Path to SQLite database for persistence. If None, uses in-memory.
        """
        self.db_path = db_path or ":memory:"
        self.corrections: Dict[str, Correction] = {}
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self._init_database()
        self._load_from_database()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Corrections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id TEXT PRIMARY KEY,
                original_question TEXT NOT NULL,
                original_sql TEXT,
                clarification TEXT NOT NULL,
                corrected_sql TEXT,
                correction_type TEXT,
                entity_mappings TEXT,  -- JSON
                filter_additions TEXT,  -- JSON
                column_changes TEXT,    -- JSON
                pattern_signature TEXT,
                confidence TEXT DEFAULT 'low',
                confirmation_count INTEGER DEFAULT 1,
                created_at TEXT,
                last_used TEXT,
                success_rate REAL DEFAULT 0.0
            )
        """)
        
        # Error patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_patterns (
                pattern_id TEXT PRIMARY KEY,
                keywords TEXT,  -- JSON
                error_description TEXT,
                suggested_fix TEXT,
                occurrence_count INTEGER DEFAULT 1,
                examples TEXT,  -- JSON
                resolution_sql_template TEXT
            )
        """)
        
        # Feedback history for tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                question TEXT,
                original_response TEXT,
                clarification TEXT,
                correction_applied TEXT,
                was_successful INTEGER,
                created_at TEXT
            )
        """)
        
        # Index for faster pattern matching
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pattern_signature 
            ON corrections(pattern_signature)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_from_database(self):
        """Load existing corrections and patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load corrections
        cursor.execute("SELECT * FROM corrections")
        for row in cursor.fetchall():
            correction = Correction(
                id=row[0],
                original_question=row[1],
                original_sql=row[2],
                clarification=row[3],
                corrected_sql=row[4],
                correction_type=CorrectionType(row[5]) if row[5] else CorrectionType.OTHER,
                entity_mappings=json.loads(row[6]) if row[6] else {},
                filter_additions=json.loads(row[7]) if row[7] else [],
                column_changes=json.loads(row[8]) if row[8] else {},
                pattern_signature=row[9] or "",
                confidence=ConfidenceLevel(row[10]) if row[10] else ConfidenceLevel.LOW,
                confirmation_count=row[11] or 1,
                created_at=datetime.fromisoformat(row[12]) if row[12] else datetime.now(),
                last_used=datetime.fromisoformat(row[13]) if row[13] else None,
                success_rate=row[14] or 0.0
            )
            self.corrections[correction.id] = correction
        
        # Load error patterns
        cursor.execute("SELECT * FROM error_patterns")
        for row in cursor.fetchall():
            pattern = ErrorPattern(
                pattern_id=row[0],
                keywords=json.loads(row[1]) if row[1] else [],
                error_description=row[2] or "",
                suggested_fix=row[3] or "",
                occurrence_count=row[4] or 1,
                examples=json.loads(row[5]) if row[5] else [],
                resolution_sql_template=row[6]
            )
            self.error_patterns[pattern.pattern_id] = pattern
        
        conn.close()
        logger.info(f"Loaded {len(self.corrections)} corrections and {len(self.error_patterns)} error patterns")
    
    def learn_from_feedback(
        self,
        message_id: str,
        original_question: str,
        original_sql: str,
        original_response: Any,
        clarification: str,
        corrected_sql: Optional[str] = None
    ) -> Correction:
        """
        Learn from user feedback when a response was incorrect.
        
        Args:
            message_id: Unique ID of the message
            original_question: The original user question
            original_sql: The SQL that was generated
            original_response: The response that was marked incorrect
            clarification: User's clarification of what was wrong
            corrected_sql: Optionally, a corrected SQL query
            
        Returns:
            The created Correction object
        """
        # Generate pattern signature for quick matching
        pattern_signature = self._generate_pattern_signature(original_question, clarification)
        
        # Check if we already have a similar correction
        existing = self._find_similar_correction(pattern_signature, original_question)
        if existing:
            # Increment confirmation count and update confidence
            existing.confirmation_count += 1
            existing.confidence = self._calculate_confidence(existing.confirmation_count)
            self._save_correction(existing)
            return existing
        
        # Analyze the clarification to determine correction type
        correction_type, entity_mappings, filter_additions, column_changes = self._analyze_clarification(
            original_question, clarification, original_sql
        )
        
        # Create new correction
        correction = Correction(
            id=f"corr_{message_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            original_question=original_question,
            original_sql=original_sql,
            clarification=clarification,
            corrected_sql=corrected_sql,
            correction_type=correction_type,
            entity_mappings=entity_mappings,
            filter_additions=filter_additions,
            column_changes=column_changes,
            pattern_signature=pattern_signature,
            confidence=ConfidenceLevel.LOW,
            confirmation_count=1,
            created_at=datetime.now()
        )
        
        # Save to memory and database
        self.corrections[correction.id] = correction
        self._save_correction(correction)
        
        # Track error pattern
        self._track_error_pattern(correction)
        
        # Log feedback history
        self._log_feedback_history(
            message_id, original_question, str(original_response), 
            clarification, correction.id
        )
        
        logger.info(f"Learned new correction: {correction.id} (type: {correction_type.value})")
        return correction
    
    def apply_learned_corrections(
        self,
        question: str,
        generated_sql: str
    ) -> Tuple[str, List[str], float]:
        """
        Apply learned corrections to a generated SQL query.
        
        Args:
            question: The user's question
            generated_sql: The SQL that was generated
            
        Returns:
            Tuple of (corrected_sql, applied_corrections, confidence_score)
        """
        applied_corrections = []
        corrected_sql = generated_sql
        total_confidence = 0.0
        
        # Generate signature for the current question
        question_signature = self._generate_question_signature(question)
        
        # Find applicable corrections
        for correction in self.corrections.values():
            if self._is_correction_applicable(question, question_signature, correction):
                # Apply the correction
                corrected_sql, applied = self._apply_correction(corrected_sql, correction)
                if applied:
                    applied_corrections.append(correction.id)
                    total_confidence += self._confidence_score(correction.confidence)
        
        # Calculate average confidence
        confidence_score = total_confidence / len(applied_corrections) if applied_corrections else 0.0
        
        if applied_corrections:
            logger.info(f"Applied {len(applied_corrections)} corrections to query (confidence: {confidence_score:.2f})")
        
        return corrected_sql, applied_corrections, confidence_score
    
    def get_suggestions_for_clarification(
        self,
        question: str,
        error_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get suggestions to help user clarify their question.
        
        Args:
            question: The original question
            error_context: Optional context about what went wrong
            
        Returns:
            List of suggestion dictionaries with 'prompt' and 'description'
        """
        suggestions = []
        
        # Check for known error patterns
        for pattern in self.error_patterns.values():
            if any(kw.lower() in question.lower() for kw in pattern.keywords):
                suggestions.append({
                    "prompt": pattern.suggested_fix,
                    "description": pattern.error_description,
                    "pattern_id": pattern.pattern_id
                })
        
        # Add common clarification prompts
        common_clarifications = [
            {
                "prompt": "Which year should I focus on?",
                "description": "Specify a time period"
            },
            {
                "prompt": "Should I filter by a specific location or area?",
                "description": "Add location filter"
            },
            {
                "prompt": "Do you want to see the data grouped differently?",
                "description": "Change data grouping"
            },
            {
                "prompt": "Would you like to compare with a previous period?",
                "description": "Add comparison"
            }
        ]
        
        # Return top suggestions
        return suggestions[:5] if suggestions else common_clarifications[:3]
    
    def record_success(self, correction_id: str, was_successful: bool):
        """
        Record whether an applied correction was successful.
        
        Args:
            correction_id: ID of the correction
            was_successful: Whether the user confirmed it was correct
        """
        if correction_id in self.corrections:
            correction = self.corrections[correction_id]
            correction.last_used = datetime.now()
            
            # Update success rate with exponential moving average
            alpha = 0.3  # Weight for new observation
            current_success = 1.0 if was_successful else 0.0
            correction.success_rate = alpha * current_success + (1 - alpha) * correction.success_rate
            
            # Update confidence based on success rate
            if was_successful and correction.confirmation_count < 10:
                correction.confirmation_count += 1
                correction.confidence = self._calculate_confidence(correction.confirmation_count)
            
            self._save_correction(correction)
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """Get statistics about learned corrections"""
        if not self.corrections:
            return {
                "total_corrections": 0,
                "by_type": {},
                "by_confidence": {},
                "avg_success_rate": 0.0
            }
        
        by_type = {}
        by_confidence = {}
        total_success = 0.0
        
        for c in self.corrections.values():
            # By type
            type_name = c.correction_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # By confidence
            conf_name = c.confidence.value
            by_confidence[conf_name] = by_confidence.get(conf_name, 0) + 1
            
            total_success += c.success_rate
        
        return {
            "total_corrections": len(self.corrections),
            "total_error_patterns": len(self.error_patterns),
            "by_type": by_type,
            "by_confidence": by_confidence,
            "avg_success_rate": total_success / len(self.corrections)
        }
    
    # =========================================================================
    # Private helper methods
    # =========================================================================
    
    def _generate_pattern_signature(self, question: str, clarification: str) -> str:
        """Generate a signature for pattern matching"""
        # Normalize and combine
        normalized = f"{question.lower().strip()}|{clarification.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _generate_question_signature(self, question: str) -> str:
        """Generate a signature for just the question"""
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _find_similar_correction(self, signature: str, question: str) -> Optional[Correction]:
        """Find an existing correction with similar pattern"""
        # Exact signature match
        for c in self.corrections.values():
            if c.pattern_signature == signature:
                return c
        
        # Fuzzy question matching (simple overlap for now)
        question_words = set(question.lower().split())
        for c in self.corrections.values():
            original_words = set(c.original_question.lower().split())
            overlap = len(question_words & original_words) / max(len(question_words), 1)
            if overlap > 0.8:  # 80% word overlap
                return c
        
        return None
    
    def _analyze_clarification(
        self,
        question: str,
        clarification: str,
        sql: str
    ) -> Tuple[CorrectionType, Dict[str, str], List[str], Dict[str, str]]:
        """Analyze clarification to determine correction type and extract details"""
        clarification_lower = clarification.lower()
        
        # Initialize results
        correction_type = CorrectionType.OTHER
        entity_mappings = {}
        filter_additions = []
        column_changes = {}
        
        # Detect correction type from keywords
        if any(kw in clarification_lower for kw in ["wrong data", "incorrect data", "not the right"]):
            correction_type = CorrectionType.WRONG_DATA
        elif any(kw in clarification_lower for kw in ["misunderstood", "didn't understand", "wrong interpretation"]):
            correction_type = CorrectionType.WRONG_INTERPRETATION
        elif any(kw in clarification_lower for kw in ["filter", "only for", "just the", "specific"]):
            correction_type = CorrectionType.MISSING_FILTERS
        elif any(kw in clarification_lower for kw in ["wrong column", "different column", "show me"]):
            correction_type = CorrectionType.WRONG_COLUMNS
        elif any(kw in clarification_lower for kw in ["total", "average", "sum", "count", "group"]):
            correction_type = CorrectionType.WRONG_AGGREGATION
        elif any(kw in clarification_lower for kw in ["year", "month", "date", "period", "2024", "2023"]):
            correction_type = CorrectionType.WRONG_TIME_RANGE
        elif any(kw in clarification_lower for kw in ["location", "neighborhood", "area", "inspector"]):
            correction_type = CorrectionType.WRONG_ENTITY
        elif any(kw in clarification_lower for kw in ["format", "table", "chart", "display"]):
            correction_type = CorrectionType.FORMATTING_ISSUE
        
        # Extract entity mentions (simple pattern matching)
        entity_keywords = {
            "location": ["at location", "for location", "at site"],
            "neighborhood": ["in neighborhood", "in area", "district"],
            "inspector": ["inspector", "by inspector", "reporter"],
            "year": ["in year", "for year", "during"]
        }
        
        for entity_type, patterns in entity_keywords.items():
            for pattern in patterns:
                if pattern in clarification_lower:
                    # Try to extract the value after the pattern
                    idx = clarification_lower.find(pattern)
                    remaining = clarification[idx + len(pattern):].strip()
                    if remaining:
                        # Take first few words as the value
                        value = " ".join(remaining.split()[:3]).strip(".,!?")
                        if value:
                            entity_mappings[entity_type] = value
        
        return correction_type, entity_mappings, filter_additions, column_changes
    
    def _calculate_confidence(self, confirmation_count: int) -> ConfidenceLevel:
        """Calculate confidence level based on confirmation count"""
        if confirmation_count >= 5:
            return ConfidenceLevel.HIGH
        elif confirmation_count >= 2:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
    
    def _confidence_score(self, confidence: ConfidenceLevel) -> float:
        """Convert confidence level to numeric score"""
        scores = {
            ConfidenceLevel.LOW: 0.3,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.HIGH: 0.9
        }
        return scores.get(confidence, 0.3)
    
    def _is_correction_applicable(
        self,
        question: str,
        question_signature: str,
        correction: Correction
    ) -> bool:
        """Check if a correction should be applied to this question"""
        # Must have reasonable confidence
        if correction.confidence == ConfidenceLevel.LOW and correction.success_rate < 0.5:
            return False
        
        # Check word overlap
        question_words = set(question.lower().split())
        original_words = set(correction.original_question.lower().split())
        overlap = len(question_words & original_words) / max(len(question_words), 1)
        
        return overlap > 0.6  # 60% overlap threshold
    
    def _apply_correction(
        self,
        sql: str,
        correction: Correction
    ) -> Tuple[str, bool]:
        """Apply a correction to SQL query"""
        modified = sql
        applied = False
        
        # Apply corrected SQL if available
        if correction.corrected_sql:
            modified = correction.corrected_sql
            applied = True
        else:
            # Apply filter additions
            for filter_clause in correction.filter_additions:
                if filter_clause not in sql:
                    # Add to WHERE clause
                    if "WHERE" in sql.upper():
                        modified = sql.replace("WHERE", f"WHERE {filter_clause} AND ")
                    else:
                        # Find FROM clause and add WHERE after it
                        from_idx = modified.upper().find("FROM")
                        if from_idx > 0:
                            # Find end of FROM clause (table name)
                            rest = modified[from_idx:]
                            end_from = rest.find("\n") if "\n" in rest else len(rest)
                            modified = modified[:from_idx + end_from] + f"\nWHERE {filter_clause}" + modified[from_idx + end_from:]
                    applied = True
            
            # Apply column changes
            for old_col, new_col in correction.column_changes.items():
                if old_col in sql:
                    modified = sql.replace(old_col, new_col)
                    applied = True
        
        return modified, applied
    
    def _track_error_pattern(self, correction: Correction):
        """Track error pattern for analytics"""
        # Create pattern from correction type and keywords
        keywords = correction.original_question.lower().split()[:5]  # First 5 words
        pattern_key = f"{correction.correction_type.value}_{'-'.join(keywords[:3])}"
        
        if pattern_key in self.error_patterns:
            # Update existing pattern
            pattern = self.error_patterns[pattern_key]
            pattern.occurrence_count += 1
            pattern.examples.append({
                "question": correction.original_question,
                "clarification": correction.clarification
            })
            # Keep only last 10 examples
            pattern.examples = pattern.examples[-10:]
        else:
            # Create new pattern
            pattern = ErrorPattern(
                pattern_id=pattern_key,
                keywords=keywords,
                error_description=f"Common {correction.correction_type.value} error",
                suggested_fix=correction.clarification,
                occurrence_count=1,
                examples=[{
                    "question": correction.original_question,
                    "clarification": correction.clarification
                }]
            )
            self.error_patterns[pattern_key] = pattern
        
        self._save_error_pattern(pattern)
    
    def _save_correction(self, correction: Correction):
        """Save correction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO corrections 
            (id, original_question, original_sql, clarification, corrected_sql,
             correction_type, entity_mappings, filter_additions, column_changes,
             pattern_signature, confidence, confirmation_count, created_at, 
             last_used, success_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            correction.id,
            correction.original_question,
            correction.original_sql,
            correction.clarification,
            correction.corrected_sql,
            correction.correction_type.value,
            json.dumps(correction.entity_mappings),
            json.dumps(correction.filter_additions),
            json.dumps(correction.column_changes),
            correction.pattern_signature,
            correction.confidence.value,
            correction.confirmation_count,
            correction.created_at.isoformat(),
            correction.last_used.isoformat() if correction.last_used else None,
            correction.success_rate
        ))
        
        conn.commit()
        conn.close()
    
    def _save_error_pattern(self, pattern: ErrorPattern):
        """Save error pattern to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO error_patterns
            (pattern_id, keywords, error_description, suggested_fix,
             occurrence_count, examples, resolution_sql_template)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern.pattern_id,
            json.dumps(pattern.keywords),
            pattern.error_description,
            pattern.suggested_fix,
            pattern.occurrence_count,
            json.dumps(pattern.examples),
            pattern.resolution_sql_template
        ))
        
        conn.commit()
        conn.close()
    
    def _log_feedback_history(
        self,
        message_id: str,
        question: str,
        original_response: str,
        clarification: str,
        correction_id: str
    ):
        """Log feedback for history tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback_history
            (message_id, question, original_response, clarification, 
             correction_applied, was_successful, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            question,
            original_response[:1000],  # Truncate long responses
            clarification,
            correction_id,
            None,  # Will be updated when user confirms
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()


# Singleton instance for global access
_correction_learner: Optional[CorrectionLearner] = None


def get_correction_learner(db_path: Optional[str] = None) -> CorrectionLearner:
    """Get or create the global correction learner instance"""
    global _correction_learner
    if _correction_learner is None:
        # Default to a file in the nlp directory
        if db_path is None:
            db_path = str(Path(__file__).parent / "corrections.db")
        _correction_learner = CorrectionLearner(db_path)
    return _correction_learner
