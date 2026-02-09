"""
Inspection Chat Agent
=====================
Main orchestrator for the bilingual NL-to-SQL chatbot.
Integrates all NLP components and handles the full query pipeline.
"""

import os
import uuid
import pyodbc
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import lru_cache

from .query_parser import QueryParser
from .sql_mapper import SQLMapper
from .entity_dictionary import EntityDictionary
from .context_manager import ContextManager
from .response_generator import ResponseGenerator
from .kpi_library import KPILibrary
from .ml_predictions_library import MLPredictionsLibrary


class QueryCache:
    """Simple in-memory cache for query results with TTL."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time-to-live in seconds (default 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
    
    def _make_key(self, query: str, language: str) -> str:
        """Create a cache key from query and language."""
        normalized = query.lower().strip()
        return hashlib.md5(f"{normalized}:{language}".encode()).hexdigest()
    
    def get(self, query: str, language: str) -> Optional[Dict[str, Any]]:
        """Get cached result if exists and not expired."""
        key = self._make_key(query, language)
        
        if key in self._cache:
            # Check if expired
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                # Expired, remove it
                del self._cache[key]
                del self._timestamps[key]
        
        return None
    
    def set(self, query: str, language: str, result: Dict[str, Any]) -> None:
        """Cache a query result."""
        # Evict oldest if at max size
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        key = self._make_key(query, language)
        self._cache[key] = result
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl_seconds": self._ttl
        }


class InspectionChatAgent:
    """
    Main agent for processing bilingual inspection queries.
    
    Pipeline:
    1. Parse user query (intent, entities, time_range) using Claude
    2. Resolve follow-ups using context manager
    3. Map to appropriate SQL template
    4. Build and execute SQL query
    5. Generate bilingual response with chart config
    """
    
    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_api_key: Optional[str] = None
    ):
        """
        Initialize the chat agent.
        
        Args:
            db_connection_string: SQL Server connection string
            azure_endpoint: Azure OpenAI endpoint for Claude
            azure_api_key: Azure OpenAI API key
        """
        # Database connection
        db_server = os.getenv("DB_SERVER", "20.3.236.169")
        db_port = os.getenv("DB_PORT", "1433")
        db_name = os.getenv("DB_NAME", "CHECK_ELM_AlUlaRC_DW")
        db_user = os.getenv("DB_USERNAME", "sa")
        db_password = os.getenv("DB_PASSWORD", "StrongPass123!")
        
        self.connection_string = db_connection_string or os.getenv(
            "DB_CONNECTION_STRING",
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={db_server},{db_port};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password};"
            f"TrustServerCertificate=yes;"
        )
        self.db_connection = None
        
        # Azure credentials
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = azure_api_key or os.getenv("AZURE_OPENAI_API_KEY")
        
        # Initialize NLP components
        self.query_parser = QueryParser(
            azure_endpoint=self.azure_endpoint,
            azure_api_key=self.azure_api_key
        )
        self.sql_mapper = SQLMapper()
        self.entity_dictionary = EntityDictionary()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator(
            azure_endpoint=self.azure_endpoint,
            azure_api_key=self.azure_api_key
        )
        self.kpi_library = None
        self.ml_library = None
        
        # Response caching for performance
        self.cache = QueryCache(max_size=100, ttl_seconds=300)
        
        # Connect to database
        self._connect_db()
    
    def _connect_db(self) -> None:
        """Establish database connection."""
        try:
            self.db_connection = pyodbc.connect(self.connection_string)
            self.kpi_library = KPILibrary(self.db_connection)
            self.ml_library = MLPredictionsLibrary(self.db_connection)
            
            # Populate entity dictionary from database
            self._refresh_entity_dictionary()
        except Exception as e:
            print(f"Database connection error: {e}")
            self.db_connection = None
    
    def _refresh_entity_dictionary(self) -> None:
        """Populate entity dictionary from database."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Load locations (using Name column which exists)
            cursor.execute("""
                SELECT DISTINCT TOP 100 Name, COALESCE(NameAr, Name) as NameAr
                FROM Locations
                WHERE Name IS NOT NULL
                  AND Isdeleted = 0
            """)
            for row in cursor.fetchall():
                if row[0] and row[1]:
                    self.entity_dictionary.add_entity(
                        "neighborhood", row[1], row[0]
                    )
            
            # Load activities/location types
            cursor.execute("""
                SELECT Name, NameAr
                FROM LocationType
                WHERE IsDeleted = 0
            """)
            for row in cursor.fetchall():
                if row[0] and row[1]:
                    self.entity_dictionary.add_entity(
                        "activity", row[1], row[0]
                    )
            
            # Load event types
            cursor.execute("""
                SELECT NameEn, NameAr
                FROM EventType
            """)
            for row in cursor.fetchall():
                if row[0] and row[1]:
                    self.entity_dictionary.add_entity(
                        "event_type", row[1], row[0]
                    )
            
            cursor.close()
        except Exception as e:
            print(f"Entity dictionary refresh error: {e}")
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process a user query through the full pipeline.
        
        Args:
            query: User's natural language query (Arabic or English)
            session_id: Session identifier for context tracking
            language: Response language preference ('en' or 'ar')
            
        Returns:
            Dict containing:
            - response: Natural language response
            - response_ar: Arabic response (if language is 'ar')
            - data: Query result data
            - chart_config: Chart configuration (if applicable)
            - template_id: SQL template used
            - session_id: Session identifier
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Check cache first (for performance)
            cached = self.cache.get(query, language)
            if cached:
                # Return cached result with fresh session_id
                cached["session_id"] = session_id
                cached["cached"] = True
                return cached
            
            # Step 1: Parse the query using Claude
            parsed = self.query_parser.parse(query)
            
            # Step 2: Resolve follow-ups using context
            resolved = self.context_manager.resolve_followup(session_id, parsed)
            
            # Step 3: Map to SQL template
            template_id, template = self.sql_mapper.map(resolved)
            
            # Step 4: Build executable SQL
            sql = self.sql_mapper.build_query(template_id, template, resolved)
            
            # Step 5: Execute query
            data = self._execute_query(sql)
            
            # Step 5.5: Use template's default_chart if available (override parser's choice)
            if template.get('default_chart'):
                resolved['chart_type'] = template['default_chart']
            if template.get('colorBy'):
                resolved['colorBy'] = template['colorBy']
            
            # Step 6: Generate response with chart
            response = self.response_generator.generate(
                parsed_query=resolved,
                data=data,
                language=language
            )
            
            # Step 7: Store in context for follow-ups
            self.context_manager.add_turn(
                session_id=session_id,
                user_query=query,
                parsed_query=resolved,
                response=response.get("message", "")
            )
            
            result = {
                "response": response.get("message", ""),
                "response_en": response.get("message_en", ""),
                "response_ar": response.get("message_ar", ""),
                "data": data,
                "chart_config": response.get("chart"),
                "recommendations": response.get("recommendations", []),
                "template_id": template_id,
                "session_id": session_id,
                "intent": resolved.get("intent"),
                "entities": resolved.get("entities"),
                "sql": sql,  # For debugging, can be removed in production
                "cached": False
            }
            
            # Cache the result for future requests
            self.cache.set(query, language, result)
            
            return result
            
        except Exception as e:
            return {
                "response": f"I encountered an error processing your query: {str(e)}",
                "response_ar": f"حدث خطأ أثناء معالجة استفسارك: {str(e)}",
                "error": str(e),
                "session_id": session_id
            }
    
    def _execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dicts."""
        if not self.db_connection:
            self._connect_db()
        
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(sql)
            
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            cursor.close()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Query execution error: {e}")
            print(f"SQL: {sql}")
            return []
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        return self.context_manager.get_history(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """Clear session context."""
        self.context_manager.clear_session(session_id)
    
    def get_kpi(self, kpi_id: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a calculated KPI value."""
        if self.kpi_library:
            return self.kpi_library.calculate_kpi(kpi_id, year)
        return None
    
    def get_all_kpis(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all calculated KPI values."""
        if self.kpi_library:
            return self.kpi_library.calculate_all_kpis(year)
        return []
    
    def get_high_risk_locations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get high-risk locations from ML predictions."""
        if self.ml_library:
            return self.ml_library.get_high_risk_locations(limit) or []
        return []
    
    def get_template_count(self) -> int:
        """Get the number of available SQL templates."""
        return self.sql_mapper.get_template_count()
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of all components."""
        return {
            "database": self.db_connection is not None,
            "templates": self.sql_mapper.get_template_count(),
            "entities": len(self.entity_dictionary._cache) if hasattr(self.entity_dictionary, '_cache') else 0,
            "azure_configured": bool(self.azure_endpoint and self.azure_api_key),
            "cache": self.cache.stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_cache(self) -> None:
        """Clear the query result cache."""
        self.cache.clear()
    
    def close(self) -> None:
        """Close database connection."""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None


# Synchronous wrapper for non-async contexts
class InspectionChatAgentSync:
    """Synchronous wrapper for InspectionChatAgent."""
    
    def __init__(self, *args, **kwargs):
        self._agent = InspectionChatAgent(*args, **kwargs)
    
    def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Process query synchronously."""
        import asyncio
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a new loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self._agent.process_query(query, session_id, language)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self._agent.process_query(query, session_id, language)
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(
                self._agent.process_query(query, session_id, language)
            )
    
    def __getattr__(self, name):
        """Delegate to wrapped agent."""
        return getattr(self._agent, name)
