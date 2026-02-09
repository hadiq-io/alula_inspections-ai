"""
Context Manager - In-memory conversation context per session
============================================================
Maintains conversation history for follow-up question handling.
Designed with Redis-ready interface for Phase 3 cloud migration.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import uuid


class ContextManager:
    """
    In-memory session context manager.
    Tracks conversation history per session for follow-up handling.
    
    Phase 3: Replace _sessions dict with Redis for cloud deployment.
    """
    
    def __init__(self, max_turns: int = 10, session_ttl_hours: int = 24):
        self._sessions: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self.max_turns = max_turns
        self.session_ttl = timedelta(hours=session_ttl_hours)
        
    def create_session(self) -> str:
        """Create a new session and return its ID"""
        session_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[session_id] = {
                'created_at': datetime.now(),
                'last_active': datetime.now(),
                'turns': [],
                'language': 'en',
                'last_query': None,
                'last_entities': {}
            }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data, creating if doesn't exist"""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    'created_at': datetime.now(),
                    'last_active': datetime.now(),
                    'turns': [],
                    'language': 'en',
                    'last_query': None,
                    'last_entities': {}
                }
            return self._sessions.get(session_id)
    
    def add_turn(self, session_id: str, user_query: str, parsed_query: Dict, 
                 response: str, data: Any = None) -> None:
        """
        Add a conversation turn to the session.
        
        Args:
            session_id: Session identifier
            user_query: Original user query text
            parsed_query: Structured query from parser
            response: AI response text
            data: Query result data (optional)
        """
        session = self.get_session(session_id)
        if not session:
            return
            
        with self._lock:
            turn = {
                'timestamp': datetime.now().isoformat(),
                'user_query': user_query,
                'parsed': parsed_query,
                'response': response,
                'data_shape': self._summarize_data(data) if data else None
            }
            
            session['turns'].append(turn)
            session['last_active'] = datetime.now()
            session['last_query'] = parsed_query
            session['last_entities'] = parsed_query.get('entities', {})
            session['language'] = parsed_query.get('language', 'en')
            
            # Trim to max turns
            if len(session['turns']) > self.max_turns:
                session['turns'] = session['turns'][-self.max_turns:]
    
    def get_history(self, session_id: str, last_n: int = 4) -> List[Dict]:
        """
        Get recent conversation history for context.
        
        Returns list of {role, content} dicts for Claude context.
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        history = []
        for turn in session['turns'][-last_n:]:
            history.append({
                'role': 'user',
                'content': turn['user_query']
            })
            history.append({
                'role': 'assistant', 
                'content': turn['response']
            })
        
        return history
    
    def get_last_entities(self, session_id: str) -> Dict:
        """Get entities from the last query for follow-up resolution"""
        session = self.get_session(session_id)
        return session.get('last_entities', {}) if session else {}
    
    def get_last_query(self, session_id: str) -> Optional[Dict]:
        """Get the full parsed query from the last turn"""
        session = self.get_session(session_id)
        return session.get('last_query') if session else None
    
    def get_language(self, session_id: str) -> str:
        """Get the current language preference for the session"""
        session = self.get_session(session_id)
        return session.get('language', 'en') if session else 'en'
    
    def set_language(self, session_id: str, language: str) -> None:
        """Set the language preference for the session"""
        session = self.get_session(session_id)
        if session:
            with self._lock:
                session['language'] = language
    
    def resolve_followup(self, session_id: str, parsed_query: Dict) -> Dict:
        """
        Resolve follow-up references using previous context.
        
        Handles queries like:
        - "ماذا عن الأندلس؟" (What about Al-Andalus?) - neighborhood change
        - "How about 2023?" - year change
        - "And restaurants?" - activity filter add
        
        Returns enhanced parsed_query with inherited entities.
        """
        last_query = self.get_last_query(session_id)
        if not last_query:
            return parsed_query
        
        # Check if this is a follow-up (has some null entities that previous had)
        is_followup = self._detect_followup(parsed_query)
        
        if not is_followup:
            return parsed_query
        
        # Inherit missing entities from previous query
        enhanced = parsed_query.copy()
        
        # Inherit metric if not specified
        if not enhanced.get('metric') and last_query.get('metric'):
            enhanced['metric'] = last_query['metric']
        
        # Inherit intent if query seems like a continuation
        if enhanced.get('intent') == 'COUNT' and last_query.get('intent'):
            enhanced['intent'] = last_query['intent']
        
        # Inherit time period if not specified
        if not enhanced.get('time_period', {}).get('year'):
            enhanced['time_period'] = enhanced.get('time_period', {})
            enhanced['time_period']['year'] = last_query.get('time_period', {}).get('year')
        
        # Inherit entities that aren't explicitly changed
        last_entities = last_query.get('entities', {})
        current_entities = enhanced.get('entities', {})
        
        for key in ['activity', 'status', 'severity']:
            if not current_entities.get(key) and last_entities.get(key):
                current_entities[key] = last_entities[key]
        
        enhanced['entities'] = current_entities
        enhanced['is_followup'] = True
        
        return enhanced
    
    def _detect_followup(self, parsed_query: Dict) -> bool:
        """Detect if a query is a follow-up to previous"""
        # Check for follow-up indicators
        query_text = parsed_query.get('original_query', '').lower()
        
        followup_indicators = [
            'what about', 'how about', 'and ', 'also ', 
            'ماذا عن', 'وماذا', 'أيضا', 'كذلك'
        ]
        
        for indicator in followup_indicators:
            if indicator in query_text:
                return True
        
        # Check if query has minimal entities (likely referencing previous)
        entities = parsed_query.get('entities', {})
        non_null_entities = sum(1 for v in entities.values() if v)
        
        if non_null_entities <= 1 and parsed_query.get('intent') in ['COUNT', 'FILTER']:
            return True
        
        return False
    
    def _summarize_data(self, data: Any) -> Dict:
        """Summarize data shape for context (don't store full data)"""
        if isinstance(data, list):
            return {'type': 'list', 'count': len(data)}
        elif isinstance(data, dict):
            return {'type': 'dict', 'keys': list(data.keys())[:5]}
        else:
            return {'type': str(type(data).__name__)}
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session's history"""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]['turns'] = []
                self._sessions[session_id]['last_query'] = None
                self._sessions[session_id]['last_entities'] = {}
                return True
        return False
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count removed."""
        now = datetime.now()
        expired = []
        
        with self._lock:
            for sid, session in self._sessions.items():
                if now - session['last_active'] > self.session_ttl:
                    expired.append(sid)
            
            for sid in expired:
                del self._sessions[sid]
        
        return len(expired)
    
    def stats(self) -> Dict:
        """Get context manager statistics"""
        return {
            'active_sessions': len(self._sessions),
            'total_turns': sum(len(s['turns']) for s in self._sessions.values())
        }
