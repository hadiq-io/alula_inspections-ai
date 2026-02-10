"""
Enhanced Context Manager v2.0 - Long-Term Memory & Preference Learning
=======================================================================
Advanced conversation context management with persistent memory,
user preference learning, and intelligent follow-up handling.

Features:
- Session-based conversation history
- Long-term memory persistence (SQLite)
- User preference learning
- Entity tracking across sessions
- Follow-up question resolution
- Conversation summarization
- Multi-session context aggregation

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import json
import sqlite3
import threading
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    id: str
    timestamp: str
    user_query: str
    parsed_query: Dict[str, Any]
    response: str
    data_summary: Optional[Dict] = None
    source: str = "template"  # template, dynamic, learned
    execution_time_ms: int = 0
    success: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationTurn':
        return cls(**data)


@dataclass
class UserPreferences:
    """Learned user preferences."""
    preferred_language: str = "en"
    preferred_chart_types: Dict[str, int] = field(default_factory=dict)  # chart_type -> count
    frequent_entities: Dict[str, Dict[str, int]] = field(default_factory=dict)  # entity_type -> {value: count}
    frequent_intents: Dict[str, int] = field(default_factory=dict)  # intent -> count
    common_time_periods: Dict[str, int] = field(default_factory=dict)  # period -> count
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update_from_query(self, parsed: Dict) -> None:
        """Update preferences from a parsed query."""
        # Update language
        if parsed.get("language"):
            self.preferred_language = parsed["language"]
        
        # Update chart preference
        chart = parsed.get("chart_type")
        if chart:
            self.preferred_chart_types[chart] = self.preferred_chart_types.get(chart, 0) + 1
        
        # Update intent frequency
        intent = parsed.get("intent")
        if intent:
            self.frequent_intents[intent] = self.frequent_intents.get(intent, 0) + 1
        
        # Update entity frequencies
        entities = parsed.get("entities", {})
        for entity_type, value in entities.items():
            if value:
                if entity_type not in self.frequent_entities:
                    self.frequent_entities[entity_type] = {}
                self.frequent_entities[entity_type][str(value)] = \
                    self.frequent_entities[entity_type].get(str(value), 0) + 1
        
        # Update time period frequencies
        time_period = parsed.get("time_period", {})
        if time_period.get("year"):
            year_key = str(time_period["year"])
            self.common_time_periods[year_key] = self.common_time_periods.get(year_key, 0) + 1
        
        self.last_updated = datetime.now().isoformat()
    
    def get_preferred_chart(self) -> str:
        """Get most preferred chart type."""
        if not self.preferred_chart_types:
            return "bar"
        return max(self.preferred_chart_types, key=self.preferred_chart_types.get)
    
    def get_frequent_entity(self, entity_type: str) -> Optional[str]:
        """Get most frequently used entity value of a type."""
        if entity_type not in self.frequent_entities:
            return None
        entities = self.frequent_entities[entity_type]
        if not entities:
            return None
        return max(entities, key=entities.get)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreferences':
        return cls(**data)


class SessionContext:
    """In-memory context for a single session."""
    
    def __init__(self, session_id: str, max_turns: int = 10):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.language = "en"
        self.turns: List[ConversationTurn] = []
        self.max_turns = max_turns
        self.last_query: Optional[Dict] = None
        self.last_entities: Dict = {}
        self.entity_history: Dict[str, List[str]] = defaultdict(list)  # Track entity values over time
        self.preferences = UserPreferences()
    
    def add_turn(
        self,
        user_query: str,
        parsed_query: Dict,
        response: str,
        data: Any = None,
        source: str = "template",
        execution_time_ms: int = 0
    ) -> ConversationTurn:
        """Add a conversation turn."""
        turn = ConversationTurn(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            parsed_query=parsed_query,
            response=response,
            data_summary=self._summarize_data(data) if data else None,
            source=source,
            execution_time_ms=execution_time_ms
        )
        
        self.turns.append(turn)
        self.last_active = datetime.now()
        self.last_query = parsed_query
        self.last_entities = parsed_query.get("entities", {})
        self.language = parsed_query.get("language", self.language)
        
        # Update entity history
        for entity_type, value in self.last_entities.items():
            if value:
                self.entity_history[entity_type].append(str(value))
        
        # Update preferences
        self.preferences.update_from_query(parsed_query)
        
        # Trim to max turns
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
        
        return turn
    
    def _summarize_data(self, data: Any) -> Dict:
        """Create a summary of data for context."""
        if isinstance(data, list):
            return {
                "type": "list",
                "count": len(data),
                "sample_keys": list(data[0].keys())[:5] if data and isinstance(data[0], dict) else []
            }
        elif isinstance(data, dict):
            return {"type": "dict", "keys": list(data.keys())[:5]}
        else:
            return {"type": str(type(data).__name__)}
    
    def get_history(self, last_n: int = 4) -> List[Dict]:
        """Get recent conversation history for Claude context."""
        history = []
        for turn in self.turns[-last_n:]:
            history.append({"role": "user", "content": turn.user_query})
            history.append({"role": "assistant", "content": turn.response})
        return history
    
    def get_conversation_summary(self) -> str:
        """Get a text summary of the conversation."""
        if not self.turns:
            return "No conversation history."
        
        summary_parts = [f"Session started: {self.created_at.isoformat()}"]
        summary_parts.append(f"Total turns: {len(self.turns)}")
        summary_parts.append(f"Language: {self.language}")
        
        # Recent queries
        recent = self.turns[-3:]
        summary_parts.append("\nRecent queries:")
        for turn in recent:
            intent = turn.parsed_query.get("intent", "unknown")
            summary_parts.append(f"  - [{intent}] {turn.user_query[:50]}...")
        
        return "\n".join(summary_parts)
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "language": self.language,
            "turns": [t.to_dict() for t in self.turns],
            "last_query": self.last_query,
            "last_entities": self.last_entities,
            "preferences": self.preferences.to_dict()
        }


class EnhancedContextManager:
    """
    Enhanced context manager with long-term memory.
    
    Features:
    - In-memory session contexts (fast)
    - SQLite persistence for long-term memory
    - Cross-session preference learning
    - Intelligent follow-up resolution
    - Entity tracking and suggestion
    """
    
    def __init__(
        self,
        max_turns: int = 10,
        session_ttl_hours: int = 24,
        db_path: str = None
    ):
        self._sessions: Dict[str, SessionContext] = {}
        self._lock = threading.RLock()
        self.max_turns = max_turns
        self.session_ttl = timedelta(hours=session_ttl_hours)
        
        # Long-term memory database
        if db_path is None:
            backend_dir = Path(__file__).parent.parent
            db_path = str(backend_dir / "conversation_memory.db")
        
        self.db_path = db_path
        self._init_database()
        
        # Global preferences (aggregated across users)
        self._global_preferences = UserPreferences()
        self._load_global_preferences()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for persistence."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                last_active TEXT,
                language TEXT,
                preferences TEXT
            )
        """)
        
        # Conversation turns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                timestamp TEXT,
                user_query TEXT,
                parsed_query TEXT,
                response TEXT,
                data_summary TEXT,
                source TEXT,
                execution_time_ms INTEGER,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Preferences learning table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preference_stats (
                key TEXT PRIMARY KEY,
                category TEXT,
                value TEXT,
                count INTEGER DEFAULT 0,
                last_updated TEXT
            )
        """)
        
        # Entity memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                entity_type TEXT,
                entity_value TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON turns(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entity_memory(entity_type)")
        
        conn.commit()
        conn.close()
    
    def _load_global_preferences(self) -> None:
        """Load aggregated preferences from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT category, value, count FROM preference_stats")
        for row in cursor.fetchall():
            category, value, count = row
            if category == "chart_type":
                self._global_preferences.preferred_chart_types[value] = count
            elif category == "intent":
                self._global_preferences.frequent_intents[value] = count
        
        conn.close()
    
    def _save_preference_stat(self, category: str, value: str) -> None:
        """Save/update a preference statistic."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        key = f"{category}:{value}"
        cursor.execute("""
            INSERT INTO preference_stats (key, category, value, count, last_updated)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(key) DO UPDATE SET 
                count = count + 1,
                last_updated = ?
        """, (key, category, value, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_session(self) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[session_id] = SessionContext(session_id, self.max_turns)
        return session_id
    
    def get_session(self, session_id: str) -> SessionContext:
        """Get or create a session."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionContext(session_id, self.max_turns)
            return self._sessions[session_id]
    
    def add_turn(
        self,
        session_id: str,
        user_query: str,
        parsed_query: Dict,
        response: str,
        data: Any = None,
        source: str = "template",
        execution_time_ms: int = 0
    ) -> None:
        """Add a conversation turn to a session."""
        session = self.get_session(session_id)
        turn = session.add_turn(
            user_query=user_query,
            parsed_query=parsed_query,
            response=response,
            data=data,
            source=source,
            execution_time_ms=execution_time_ms
        )
        
        # Save to long-term memory
        self._save_turn(session_id, turn)
        
        # Update global preferences
        if parsed_query.get("chart_type"):
            self._save_preference_stat("chart_type", parsed_query["chart_type"])
        if parsed_query.get("intent"):
            self._save_preference_stat("intent", parsed_query["intent"])
    
    def _save_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Save a turn to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO turns 
            (id, session_id, timestamp, user_query, parsed_query, response, 
             data_summary, source, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            turn.id, session_id, turn.timestamp, turn.user_query,
            json.dumps(turn.parsed_query), turn.response,
            json.dumps(turn.data_summary) if turn.data_summary else None,
            turn.source, turn.execution_time_ms
        ))
        
        # Save entity references
        for entity_type, value in turn.parsed_query.get("entities", {}).items():
            if value:
                cursor.execute("""
                    INSERT INTO entity_memory (session_id, entity_type, entity_value, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (session_id, entity_type, str(value), turn.timestamp))
        
        conn.commit()
        conn.close()
    
    def get_history(self, session_id: str, last_n: int = 4) -> List[Dict]:
        """Get recent conversation history."""
        session = self.get_session(session_id)
        return session.get_history(last_n)
    
    def get_last_entities(self, session_id: str) -> Dict:
        """Get entities from the last query."""
        session = self.get_session(session_id)
        return session.last_entities
    
    def get_last_query(self, session_id: str) -> Optional[Dict]:
        """Get the last parsed query."""
        session = self.get_session(session_id)
        return session.last_query
    
    def get_language(self, session_id: str) -> str:
        """Get session language preference."""
        session = self.get_session(session_id)
        return session.language
    
    def set_language(self, session_id: str, language: str) -> None:
        """Set session language preference."""
        session = self.get_session(session_id)
        session.language = language
    
    def resolve_followup(self, session_id: str, parsed_query: Dict) -> Dict:
        """
        Resolve follow-up references using previous context.
        Enhanced with preference-based defaults and entity history.
        """
        session = self.get_session(session_id)
        last_query = session.last_query
        
        if not last_query:
            return parsed_query
        
        # Check if this is a follow-up
        is_followup = self._detect_followup(parsed_query, session)
        
        if not is_followup:
            return parsed_query
        
        # Enhanced follow-up resolution
        enhanced = parsed_query.copy()
        enhanced["is_followup"] = True
        
        # Inherit metric if not specified
        if not enhanced.get("metric") and last_query.get("metric"):
            enhanced["metric"] = last_query["metric"]
        
        # Inherit or upgrade intent
        if enhanced.get("intent") == "COUNT" and last_query.get("intent"):
            enhanced["intent"] = last_query["intent"]
        
        # Inherit time period
        if not enhanced.get("time_period", {}).get("year"):
            enhanced["time_period"] = enhanced.get("time_period", {})
            if last_query.get("time_period", {}).get("year"):
                enhanced["time_period"]["year"] = last_query["time_period"]["year"]
            elif session.preferences.common_time_periods:
                # Use user's most common time period
                most_common = max(
                    session.preferences.common_time_periods,
                    key=session.preferences.common_time_periods.get
                )
                try:
                    enhanced["time_period"]["year"] = int(most_common)
                except ValueError:
                    pass
        
        # Inherit entities with smart defaults
        last_entities = last_query.get("entities", {})
        current_entities = enhanced.get("entities", {})
        
        for key in ["activity", "status", "severity"]:
            if not current_entities.get(key):
                if last_entities.get(key):
                    current_entities[key] = last_entities[key]
                elif key in session.entity_history and session.entity_history[key]:
                    # Use most recent entity of this type
                    current_entities[key] = session.entity_history[key][-1]
        
        enhanced["entities"] = current_entities
        
        return enhanced
    
    def _detect_followup(self, parsed_query: Dict, session: SessionContext) -> bool:
        """Detect if a query is a follow-up."""
        query_text = parsed_query.get("original_query", "").lower()
        
        # Explicit follow-up indicators
        followup_indicators = [
            # English
            "what about", "how about", "and ", "also ", "but what",
            "same for", "now show", "tell me more", "more details",
            # Arabic
            "ماذا عن", "وماذا", "أيضا", "كذلك", "المزيد", "أخبرني"
        ]
        
        for indicator in followup_indicators:
            if indicator in query_text:
                return True
        
        # Check if minimal new entities (referencing previous)
        entities = parsed_query.get("entities", {})
        non_null = sum(1 for v in entities.values() if v)
        
        # If only 1 entity changed and we have history, it's likely a follow-up
        if non_null <= 1 and len(session.turns) > 0:
            return True
        
        return False
    
    def get_entity_suggestions(self, session_id: str, entity_type: str, limit: int = 5) -> List[str]:
        """Get suggested entity values based on history."""
        # First check session history
        session = self.get_session(session_id)
        if entity_type in session.entity_history:
            recent = session.entity_history[entity_type][-limit:]
            if recent:
                return list(set(recent))
        
        # Fall back to global memory
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT entity_value, COUNT(*) as cnt
            FROM entity_memory
            WHERE entity_type = ?
            GROUP BY entity_value
            ORDER BY cnt DESC
            LIMIT ?
        """, (entity_type, limit))
        
        suggestions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return suggestions
    
    def get_preferred_chart(self, session_id: str) -> str:
        """Get preferred chart type for session."""
        session = self.get_session(session_id)
        
        # Session preference first
        session_pref = session.preferences.get_preferred_chart()
        if session.preferences.preferred_chart_types:
            return session_pref
        
        # Fall back to global preference
        return self._global_preferences.get_preferred_chart()
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session's history."""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id] = SessionContext(session_id, self.max_turns)
                return True
        return False
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        now = datetime.now()
        expired = []
        
        with self._lock:
            for sid, session in self._sessions.items():
                if now - session.last_active > self.session_ttl:
                    # Save to long-term memory before removing
                    self._persist_session(session)
                    expired.append(sid)
            
            for sid in expired:
                del self._sessions[sid]
        
        return len(expired)
    
    def _persist_session(self, session: SessionContext) -> None:
        """Persist a session to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (session_id, created_at, last_active, language, preferences)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.created_at.isoformat(),
            session.last_active.isoformat(),
            session.language,
            json.dumps(session.preferences.to_dict())
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_context(self, session_id: str) -> str:
        """Get a text context summary for AI prompting."""
        session = self.get_session(session_id)
        
        if not session.turns:
            return ""
        
        lines = ["Previous conversation context:"]
        
        for turn in session.turns[-3:]:
            intent = turn.parsed_query.get("intent", "")
            entities = turn.parsed_query.get("entities", {})
            entity_str = ", ".join(f"{k}={v}" for k, v in entities.items() if v)
            lines.append(f"Q: {turn.user_query[:100]}")
            lines.append(f"   Intent: {intent}, Entities: {entity_str}")
        
        return "\n".join(lines)
    
    def stats(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM turns")
        total_turns = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM turns WHERE timestamp > datetime('now', '-24 hours')")
        active_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "active_sessions": len(self._sessions),
            "total_sessions_stored": total_sessions,
            "total_turns_stored": total_turns,
            "active_last_24h": active_24h,
            "session_ttl_hours": self.session_ttl.total_seconds() / 3600
        }


# Backward compatibility alias
ContextManager = EnhancedContextManager
