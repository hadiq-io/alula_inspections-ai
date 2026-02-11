"""
Query Learning System - Self-Improving Query Library
====================================================
Captures successful dynamically generated queries and promotes them
to permanent templates. The system learns from usage patterns.

Features:
- Captures successful dynamic queries
- Tracks usage frequency and success rate
- Auto-promotes queries after threshold
- Pattern matching for similar questions
- Query variation detection
- Performance-based ranking

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import json
import re
import hashlib
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path
import sqlite3


@dataclass
class LearnedQuery:
    """A learned query with usage statistics."""
    id: str
    pattern: str  # Normalized question pattern
    sql: str
    explanation_en: str
    explanation_ar: str
    
    # Metadata
    original_question: str
    intent: Optional[str] = None
    entities_pattern: Dict[str, str] = field(default_factory=dict)
    tables_used: List[str] = field(default_factory=list)
    chart_type: str = "bar"
    
    # Statistics
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used_at: str = field(default_factory=lambda: datetime.now().isoformat())
    use_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time_ms: float = 0.0
    
    # Promotion status
    is_promoted: bool = False  # Promoted to permanent template
    promotion_date: Optional[str] = None
    confidence_score: float = 0.0
    
    # User validation fields
    user_validated: bool = False  # True if user explicitly validated
    validation_source: str = "auto"  # "auto" or "user"
    validation_count: int = 0  # Number of user validations
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LearnedQuery':
        return cls(**data)
    
    def to_template_format(self) -> Dict[str, Any]:
        """Convert to SQL template format for permanent promotion."""
        return {
            "id": f"LEARNED_{self.id[:8].upper()}",
            "intents": [self.intent] if self.intent else ["COUNT"],
            "question_en": self.original_question,
            "question_ar": "",  # Could add Arabic translation
            "default_chart": self.chart_type,
            "sql": self.sql,
            "filters": {},
            "learned": True,
            "learned_at": self.created_at,
            "use_count": self.use_count,
            "success_rate": self.success_rate
        }


class QueryLearningSystem:
    """
    Self-improving query learning system.
    
    Workflow:
    1. Dynamic query generated and executed successfully
    2. Query captured with pattern extraction
    3. Similar queries tracked together
    4. After N successful uses, promote to permanent template
    5. Templates exported to learned.py file
    
    Storage: SQLite for persistence across restarts
    """
    
    # Promotion thresholds
    MIN_USES_FOR_PROMOTION = 3
    MIN_SUCCESS_RATE = 0.8
    MAX_AVG_EXECUTION_TIME_MS = 5000
    
    # Pattern matching settings
    SIMILARITY_THRESHOLD = 0.7
    
    def __init__(self, db_path: str = None):
        """
        Initialize the learning system.
        
        Args:
            db_path: Path to SQLite database for persistence
        """
        self._lock = threading.Lock()
        
        # Default path in backend folder
        if db_path is None:
            backend_dir = Path(__file__).parent.parent
            db_path = str(backend_dir / "learned_queries.db")
        
        self.db_path = db_path
        self._init_database()
        
        # In-memory cache for fast lookups
        self._pattern_cache: Dict[str, LearnedQuery] = {}
        self._load_cache()
    
    def _init_database(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_queries (
                id TEXT PRIMARY KEY,
                pattern TEXT NOT NULL,
                sql TEXT NOT NULL,
                explanation_en TEXT,
                explanation_ar TEXT,
                original_question TEXT,
                intent TEXT,
                entities_pattern TEXT,
                tables_used TEXT,
                chart_type TEXT DEFAULT 'bar',
                created_at TEXT,
                last_used_at TEXT,
                use_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_execution_time_ms REAL DEFAULT 0,
                is_promoted INTEGER DEFAULT 0,
                promotion_date TEXT,
                confidence_score REAL DEFAULT 0,
                user_validated INTEGER DEFAULT 0,
                validation_source TEXT DEFAULT 'auto',
                validation_count INTEGER DEFAULT 0
            )
        """)
        
        # Add new columns if they don't exist (for migration)
        try:
            cursor.execute("ALTER TABLE learned_queries ADD COLUMN user_validated INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE learned_queries ADD COLUMN validation_source TEXT DEFAULT 'auto'")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE learned_queries ADD COLUMN validation_count INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        # Index for pattern lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pattern 
            ON learned_queries(pattern)
        """)
        
        # Index for promotion candidates
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promotion 
            ON learned_queries(is_promoted, use_count, success_count)
        """)
        
        # Index for user-validated queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_validated 
            ON learned_queries(user_validated, validation_count)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_cache(self) -> None:
        """Load frequently used queries into memory cache."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load top 100 most used queries
        cursor.execute("""
            SELECT * FROM learned_queries
            ORDER BY use_count DESC
            LIMIT 100
        """)
        
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            # Parse JSON fields
            data['entities_pattern'] = json.loads(data['entities_pattern'] or '{}')
            data['tables_used'] = json.loads(data['tables_used'] or '[]')
            data['is_promoted'] = bool(data['is_promoted'])
            # Parse user validation fields
            data['user_validated'] = bool(data.get('user_validated', 0))
            data['validation_source'] = data.get('validation_source', 'auto')
            data['validation_count'] = data.get('validation_count', 0)
            
            query = LearnedQuery.from_dict(data)
            self._pattern_cache[query.pattern] = query
        
        conn.close()
    
    def capture_query(
        self,
        question: str,
        sql: str,
        explanation_en: str,
        explanation_ar: str = "",
        intent: str = None,
        entities: Dict = None,
        tables_used: List[str] = None,
        chart_type: str = "bar",
        execution_time_ms: float = 0,
        success: bool = True,
        user_validated: bool = False  # NEW: User explicitly validated this query
    ) -> LearnedQuery:
        """
        Capture a dynamically generated query for learning.
        
        Args:
            question: Original user question
            sql: Generated SQL query
            explanation_en: English explanation
            explanation_ar: Arabic explanation
            intent: Query intent (COUNT, TREND, etc.)
            entities: Entities extracted from question
            tables_used: Tables referenced in query
            chart_type: Suggested chart type
            execution_time_ms: Query execution time
            success: Whether query executed successfully
            user_validated: Whether user explicitly validated this as correct
            
        Returns:
            LearnedQuery object
        """
        pattern = self._extract_pattern(question)
        query_id = self._generate_id(pattern, sql)
        
        with self._lock:
            # Check if pattern already exists
            existing = self._find_by_pattern(pattern)
            
            if existing:
                # Update existing query stats
                existing.use_count += 1
                existing.last_used_at = datetime.now().isoformat()
                
                if success:
                    existing.success_count += 1
                else:
                    existing.failure_count += 1
                
                # Update rolling average execution time
                if execution_time_ms > 0:
                    existing.avg_execution_time_ms = (
                        (existing.avg_execution_time_ms * (existing.use_count - 1) + execution_time_ms)
                        / existing.use_count
                    )
                
                # Handle user validation - higher weight for promotion
                if user_validated:
                    existing.user_validated = True
                    existing.validation_source = "user"
                    existing.validation_count += 1
                
                # Update confidence
                existing.confidence_score = self._calculate_confidence(existing)
                
                # Save update
                self._save_query(existing)
                
                # Check for promotion (user-validated queries promote faster)
                self._check_promotion(existing)
                
                return existing
            
            else:
                # Create new learned query
                new_query = LearnedQuery(
                    id=query_id,
                    pattern=pattern,
                    sql=sql,
                    explanation_en=explanation_en,
                    explanation_ar=explanation_ar,
                    original_question=question,
                    intent=intent,
                    entities_pattern=self._extract_entity_pattern(entities or {}),
                    tables_used=tables_used or [],
                    chart_type=chart_type,
                    use_count=1,
                    success_count=1 if success else 0,
                    failure_count=0 if success else 1,
                    avg_execution_time_ms=execution_time_ms,
                    confidence_score=0.8 if user_validated else 0.5,  # Higher confidence if user-validated
                    user_validated=user_validated,
                    validation_source="user" if user_validated else "auto",
                    validation_count=1 if user_validated else 0
                )
                
                # Save to database
                self._save_query(new_query)
                
                # Add to cache
                self._pattern_cache[pattern] = new_query
                
                return new_query
    
    def find_matching_query(self, question: str) -> Optional[LearnedQuery]:
        """
        Find a learned query that matches the question.
        
        Args:
            question: User's question
            
        Returns:
            Matching LearnedQuery or None
        """
        pattern = self._extract_pattern(question)
        
        # Exact match in cache
        if pattern in self._pattern_cache:
            return self._pattern_cache[pattern]
        
        # Fuzzy match
        best_match = None
        best_score = 0.0
        
        for cached_pattern, query in self._pattern_cache.items():
            score = self._similarity_score(pattern, cached_pattern)
            if score > self.SIMILARITY_THRESHOLD and score > best_score:
                best_match = query
                best_score = score
        
        # If no cache hit, search database
        if not best_match:
            best_match = self._search_database(pattern)
        
        return best_match
    
    def get_learned_sql(self, question: str, entities: Dict = None) -> Optional[Tuple[str, LearnedQuery]]:
        """
        Get learned SQL for a question, with entity substitution.
        
        Args:
            question: User question
            entities: Current entities to substitute
            
        Returns:
            Tuple of (substituted SQL, LearnedQuery) or None
        """
        query = self.find_matching_query(question)
        
        if not query:
            return None
        
        # Substitute entities if needed
        sql = query.sql
        if entities:
            sql = self._substitute_entities(sql, query.entities_pattern, entities)
        
        return sql, query
    
    def _extract_pattern(self, question: str) -> str:
        """Extract a normalized pattern from a question."""
        pattern = question.lower().strip()
        
        # Remove specific values to create a pattern
        # Replace years
        pattern = re.sub(r'\b20\d{2}\b', '{YEAR}', pattern)
        
        # Replace month names
        months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        ]
        for month in months:
            pattern = re.sub(rf'\b{month}\b', '{MONTH}', pattern, flags=re.IGNORECASE)
        
        # Replace Arabic month names
        arabic_months = [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        for month in arabic_months:
            pattern = pattern.replace(month, '{MONTH}')
        
        # Replace numbers
        pattern = re.sub(r'\b\d+\b', '{NUMBER}', pattern)
        
        # Replace quoted strings
        pattern = re.sub(r'"[^"]*"', '{VALUE}', pattern)
        pattern = re.sub(r"'[^']*'", '{VALUE}', pattern)
        
        # Normalize whitespace
        pattern = ' '.join(pattern.split())
        
        return pattern
    
    def _extract_entity_pattern(self, entities: Dict) -> Dict[str, str]:
        """Extract entity pattern for template matching."""
        pattern = {}
        for key, value in entities.items():
            if value:
                pattern[key] = "{" + key.upper() + "}"
        return pattern
    
    def _generate_id(self, pattern: str, sql: str) -> str:
        """Generate a unique ID for a query."""
        content = f"{pattern}::{sql}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _find_by_pattern(self, pattern: str) -> Optional[LearnedQuery]:
        """Find query by exact pattern match."""
        # Check cache first
        if pattern in self._pattern_cache:
            return self._pattern_cache[pattern]
        
        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM learned_queries WHERE pattern = ?",
            (pattern,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [
                'id', 'pattern', 'sql', 'explanation_en', 'explanation_ar',
                'original_question', 'intent', 'entities_pattern', 'tables_used',
                'chart_type', 'created_at', 'last_used_at', 'use_count',
                'success_count', 'failure_count', 'avg_execution_time_ms',
                'is_promoted', 'promotion_date', 'confidence_score'
            ]
            data = dict(zip(columns, row))
            data['entities_pattern'] = json.loads(data['entities_pattern'] or '{}')
            data['tables_used'] = json.loads(data['tables_used'] or '[]')
            data['is_promoted'] = bool(data['is_promoted'])
            
            query = LearnedQuery.from_dict(data)
            self._pattern_cache[pattern] = query
            return query
        
        return None
    
    def _save_query(self, query: LearnedQuery) -> None:
        """Save or update a query in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO learned_queries (
                id, pattern, sql, explanation_en, explanation_ar,
                original_question, intent, entities_pattern, tables_used,
                chart_type, created_at, last_used_at, use_count,
                success_count, failure_count, avg_execution_time_ms,
                is_promoted, promotion_date, confidence_score,
                user_validated, validation_source, validation_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query.id, query.pattern, query.sql, query.explanation_en,
            query.explanation_ar, query.original_question, query.intent,
            json.dumps(query.entities_pattern), json.dumps(query.tables_used),
            query.chart_type, query.created_at, query.last_used_at,
            query.use_count, query.success_count, query.failure_count,
            query.avg_execution_time_ms, int(query.is_promoted),
            query.promotion_date, query.confidence_score,
            int(query.user_validated), query.validation_source, query.validation_count
        ))
        
        conn.commit()
        conn.close()
    
    def _search_database(self, pattern: str) -> Optional[LearnedQuery]:
        """Search database for similar patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get potential matches
        cursor.execute("""
            SELECT * FROM learned_queries
            WHERE use_count >= 2
            ORDER BY use_count DESC
            LIMIT 50
        """)
        
        columns = [desc[0] for desc in cursor.description]
        best_match = None
        best_score = 0.0
        
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            stored_pattern = data['pattern']
            
            score = self._similarity_score(pattern, stored_pattern)
            if score > self.SIMILARITY_THRESHOLD and score > best_score:
                data['entities_pattern'] = json.loads(data['entities_pattern'] or '{}')
                data['tables_used'] = json.loads(data['tables_used'] or '[]')
                data['is_promoted'] = bool(data['is_promoted'])
                
                best_match = LearnedQuery.from_dict(data)
                best_score = score
        
        conn.close()
        return best_match
    
    def _similarity_score(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two patterns."""
        # Simple word-based Jaccard similarity
        words1 = set(pattern1.lower().split())
        words2 = set(pattern2.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _substitute_entities(
        self, sql: str, pattern_entities: Dict, actual_entities: Dict
    ) -> str:
        """Substitute entity placeholders with actual values."""
        result = sql
        
        for key, placeholder in pattern_entities.items():
            if key in actual_entities and actual_entities[key]:
                value = actual_entities[key]
                # Escape for SQL
                if isinstance(value, str):
                    value = value.replace("'", "''")
                    result = result.replace(placeholder, f"'{value}'")
                else:
                    result = result.replace(placeholder, str(value))
        
        return result
    
    def _calculate_confidence(self, query: LearnedQuery) -> float:
        """Calculate confidence score for a learned query."""
        score = 0.5  # Base score
        
        # Success rate bonus
        if query.success_rate > 0.9:
            score += 0.3
        elif query.success_rate > 0.7:
            score += 0.2
        
        # Usage count bonus
        if query.use_count >= 10:
            score += 0.15
        elif query.use_count >= 5:
            score += 0.1
        
        # Performance bonus
        if query.avg_execution_time_ms < 1000:
            score += 0.1
        elif query.avg_execution_time_ms > 5000:
            score -= 0.1
        
        return min(1.0, max(0.0, score))
    
    def _check_promotion(self, query: LearnedQuery) -> bool:
        """Check if a query should be promoted to permanent template."""
        if query.is_promoted:
            return False
        
        # User-validated queries get faster promotion (2 uses instead of 3)
        min_uses = 2 if query.user_validated else self.MIN_USES_FOR_PROMOTION
        min_success_rate = 0.7 if query.user_validated else self.MIN_SUCCESS_RATE
        
        # Check criteria
        if (query.use_count >= min_uses and
            query.success_rate >= min_success_rate and
            query.avg_execution_time_ms <= self.MAX_AVG_EXECUTION_TIME_MS):
            
            # Promote!
            query.is_promoted = True
            query.promotion_date = datetime.now().isoformat()
            self._save_query(query)
            
            # Export to templates file
            self._export_promoted_queries()
            
            validation_note = " (user-validated)" if query.user_validated else ""
            print(f"✅ Query promoted to permanent template{validation_note}: {query.id}")
            return True
        
        return False
    
    def _export_promoted_queries(self) -> None:
        """Export promoted queries to learned.py template file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM learned_queries
            WHERE is_promoted = 1
            ORDER BY use_count DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        templates = {}
        
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            data['entities_pattern'] = json.loads(data['entities_pattern'] or '{}')
            data['tables_used'] = json.loads(data['tables_used'] or '[]')
            data['is_promoted'] = bool(data['is_promoted'])
            
            query = LearnedQuery.from_dict(data)
            template = query.to_template_format()
            templates[template['id']] = template
        
        conn.close()
        
        # Write to learned.py
        self._write_templates_file(templates)
    
    def _write_templates_file(self, templates: Dict) -> None:
        """Write templates to learned.py file."""
        template_file = Path(__file__).parent / "sql_templates" / "learned.py"
        
        content = '''"""
Learned SQL Templates - Auto-generated by Query Learning System
================================================================
DO NOT EDIT MANUALLY - This file is auto-generated from successful
dynamically generated queries that have been promoted to permanent templates.

These queries were learned from user interactions and have proven
reliable through multiple successful executions.

Last updated: {timestamp}
Total templates: {count}
"""

TEMPLATES = {templates}
'''
        
        formatted = content.format(
            timestamp=datetime.now().isoformat(),
            count=len(templates),
            templates=json.dumps(templates, indent=4, ensure_ascii=False)
        )
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(formatted)
    
    def get_promotion_candidates(self) -> List[LearnedQuery]:
        """Get queries that are close to being promoted."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM learned_queries
            WHERE is_promoted = 0
              AND use_count >= 2
            ORDER BY use_count DESC, success_count DESC
            LIMIT 20
        """)
        
        columns = [desc[0] for desc in cursor.description]
        candidates = []
        
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            data['entities_pattern'] = json.loads(data['entities_pattern'] or '{}')
            data['tables_used'] = json.loads(data['tables_used'] or '[]')
            data['is_promoted'] = bool(data['is_promoted'])
            
            candidates.append(LearnedQuery.from_dict(data))
        
        conn.close()
        return candidates
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning system statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM learned_queries")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM learned_queries WHERE is_promoted = 1")
        promoted = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(use_count) FROM learned_queries")
        total_uses = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT AVG(CAST(success_count AS FLOAT) / NULLIF(use_count, 0))
            FROM learned_queries WHERE use_count > 0
        """)
        avg_success_rate = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_learned_queries": total,
            "promoted_to_templates": promoted,
            "total_uses": total_uses,
            "average_success_rate": round(avg_success_rate, 3),
            "cache_size": len(self._pattern_cache)
        }
    
    def clear_failed_queries(self, min_failures: int = 5) -> int:
        """Remove queries with too many failures."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM learned_queries
            WHERE failure_count >= ?
              AND is_promoted = 0
        """, (min_failures,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        # Refresh cache
        self._pattern_cache.clear()
        self._load_cache()
        
        return deleted


# Global singleton
_learning_system: Optional[QueryLearningSystem] = None
_learning_lock = threading.Lock()


def get_learning_system() -> QueryLearningSystem:
    """Get the global query learning system instance."""
    global _learning_system
    
    with _learning_lock:
        if _learning_system is None:
            _learning_system = QueryLearningSystem()
        return _learning_system
