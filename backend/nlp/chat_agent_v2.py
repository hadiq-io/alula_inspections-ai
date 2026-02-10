"""
Intelligent Chat Agent v2.0 - Hybrid Query System
==================================================
Enhanced chat agent with dynamic query generation, learning memory,
and intelligent query routing. Can handle ANY question, not just templates.

Architecture:
1. Parse user query with Claude
2. Check learned queries first (fastest)
3. Try template matching (fast, reliable)
4. Fall back to dynamic SQL generation (flexible)
5. Learn from successful dynamic queries
6. Monitor and track all executions

Features:
- Hybrid query routing
- Self-learning from successful queries
- Performance monitoring
- Circuit breaker protection
- Multi-tier caching
- Bilingual support (Arabic/English)

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import uuid
import time
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime

from .query_parser import QueryParser
from .sql_mapper import SQLMapper
from .entity_dictionary import EntityDictionary
from .context_manager import ContextManager
from .response_generator import ResponseGenerator
from .kpi_library import KPILibrary
from .ml_predictions_library import MLPredictionsLibrary

# New v2.0 components
from .schema_registry import get_schema_registry, SchemaRegistry
from .dynamic_sql_generator import DynamicSQLGenerator, GeneratedQuery
from .query_learning import get_learning_system, QueryLearningSystem
from .query_monitor import get_query_monitor, QueryMonitor, time_query
from .query_validator import QueryValidator


class QueryCache:
    """Simple in-memory cache for query results with TTL."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
    
    def _make_key(self, query: str, language: str) -> str:
        normalized = query.lower().strip()
        return hashlib.md5(f"{normalized}:{language}".encode()).hexdigest()
    
    def get(self, query: str, language: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(query, language)
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, query: str, language: str, result: Dict[str, Any]) -> None:
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        key = self._make_key(query, language)
        self._cache[key] = result
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        self._cache.clear()
        self._timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl_seconds": self._ttl
        }


class IntelligentChatAgent:
    """
    Intelligent chat agent with hybrid query routing and learning capabilities.
    
    Query Resolution Order:
    1. Response Cache (5 min TTL) - Fastest
    2. Learned Queries - Fast, proven reliable
    3. Template Matching (score >= 70) - Fast, reliable
    4. Dynamic SQL Generation - Flexible, handles anything
    5. Fallback with Schema Hints - Graceful degradation
    
    After successful dynamic query:
    - Capture in learning system
    - Track performance metrics
    - Promote to template after 3+ uses
    """
    
    # Confidence threshold for template matching
    TEMPLATE_CONFIDENCE_THRESHOLD = 70.0
    
    # Whether to enable dynamic SQL generation
    ENABLE_DYNAMIC_GENERATION = True
    
    # Whether to enable learning from dynamic queries
    ENABLE_LEARNING = True
    
    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_api_key: Optional[str] = None
    ):
        """Initialize the intelligent chat agent."""
        # Database connection settings
        db_server = os.getenv("DB_SERVER", "20.3.236.169")
        db_port = os.getenv("DB_PORT", "1433")
        db_name = os.getenv("DB_NAME", "CHECK_ELM_AlUlaRC_DW")
        db_user = os.getenv("DB_USERNAME", "sa")
        db_password = os.getenv("DB_PASSWORD", "StrongPass123!")
        
        self.connection_string = db_connection_string or (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={db_server},{db_port};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password};"
            f"TrustServerCertificate=yes;"
        )
        
        # Azure credentials
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = azure_api_key or os.getenv("AZURE_OPENAI_KEY")
        
        # Initialize core NLP components
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
        
        # Initialize v2.0 intelligent components
        self.schema_registry = get_schema_registry()
        self.dynamic_generator = DynamicSQLGenerator(
            schema_registry=self.schema_registry,
            azure_endpoint=self.azure_endpoint,
            azure_api_key=self.azure_api_key
        )
        self.learning_system = get_learning_system()
        self.query_monitor = get_query_monitor()
        self.validator = QueryValidator(schema_registry=self.schema_registry)
        
        # Libraries
        self.kpi_library = None
        self.ml_library = None
        
        # Response cache
        self.cache = QueryCache(max_size=100, ttl_seconds=300)
        
        # Database connection
        self.db_connection = None
        self._connect_db()
        
        # Initialize schema registry
        self.schema_registry.initialize()
        
        # Statistics
        self._stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "learned_hits": 0,
            "template_hits": 0,
            "dynamic_generations": 0,
            "fallbacks": 0,
            "errors": 0
        }
        
        print("✅ Intelligent Chat Agent v2.0 initialized")
        print(f"   - Templates: {self.sql_mapper.get_template_count()}")
        print(f"   - Learned queries: {self.learning_system.get_stats()['total_learned_queries']}")
        print(f"   - Schema tables: {self.schema_registry.stats()['total_tables']}")
    
    def _connect_db(self) -> None:
        """Establish database connection."""
        try:
            import pyodbc
            self.db_connection = pyodbc.connect(self.connection_string)
            self.kpi_library = KPILibrary(self.db_connection)
            self.ml_library = MLPredictionsLibrary(self.db_connection)
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
            
            # Load locations
            cursor.execute("""
                SELECT DISTINCT TOP 100 Name, COALESCE(NameAr, Name) as NameAr
                FROM Locations
                WHERE Name IS NOT NULL AND Isdeleted = 0
            """)
            for row in cursor.fetchall():
                if row[0] and row[1]:
                    self.entity_dictionary.add_entity("neighborhood", row[1], row[0])
            
            # Load activities
            cursor.execute("""
                SELECT Name, NameAr
                FROM LocationType
                WHERE IsDeleted = 0
            """)
            for row in cursor.fetchall():
                if row[0] and row[1]:
                    self.entity_dictionary.add_entity("activity", row[1], row[0])
            
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
        Process a user query through the intelligent hybrid pipeline.
        
        Args:
            query: User's natural language query
            session_id: Session identifier for context
            language: Response language ('en' or 'ar')
            
        Returns:
            Complete response with data, charts, and metadata
        """
        start_time = time.time()
        self._stats["total_queries"] += 1
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # ========== STEP 1: Check Response Cache ==========
            cached = self.cache.get(query, language)
            if cached:
                self._stats["cache_hits"] += 1
                cached["session_id"] = session_id
                cached["cached"] = True
                cached["source"] = "cache"
                return cached
            
            # ========== STEP 2: Parse Query ==========
            parsed = self.query_parser.parse(query)
            parsed["original_query"] = query
            
            # Resolve follow-ups from context
            resolved = self.context_manager.resolve_followup(session_id, parsed)
            
            # ========== STEP 3: Try Learned Queries ==========
            learned_result = self._try_learned_query(query, resolved)
            if learned_result:
                self._stats["learned_hits"] += 1
                result = self._build_response(
                    query=query,
                    sql=learned_result["sql"],
                    parsed=resolved,
                    language=language,
                    session_id=session_id,
                    source="learned",
                    template_id=learned_result.get("template_id")
                )
                return result
            
            # ========== STEP 4: Try Template Matching ==========
            template_result = self._try_template_matching(resolved)
            if template_result:
                self._stats["template_hits"] += 1
                result = self._build_response(
                    query=query,
                    sql=template_result["sql"],
                    parsed=resolved,
                    language=language,
                    session_id=session_id,
                    source="template",
                    template_id=template_result.get("template_id"),
                    template=template_result.get("template")
                )
                return result
            
            # ========== STEP 5: Dynamic SQL Generation ==========
            if self.ENABLE_DYNAMIC_GENERATION:
                dynamic_result = self._try_dynamic_generation(query, resolved, language)
                if dynamic_result and dynamic_result.is_valid:
                    self._stats["dynamic_generations"] += 1
                    result = self._build_response(
                        query=query,
                        sql=dynamic_result.sql,
                        parsed=resolved,
                        language=language,
                        session_id=session_id,
                        source="dynamic",
                        generated_query=dynamic_result
                    )
                    
                    # Learn from successful dynamic query
                    if self.ENABLE_LEARNING:
                        self._learn_from_query(query, dynamic_result, resolved)
                    
                    return result
            
            # ========== STEP 6: Fallback with Hints ==========
            self._stats["fallbacks"] += 1
            return self._generate_fallback_response(query, resolved, language, session_id)
            
        except Exception as e:
            self._stats["errors"] += 1
            elapsed = int((time.time() - start_time) * 1000)
            return {
                "response": f"I encountered an error: {str(e)}",
                "response_ar": f"حدث خطأ: {str(e)}",
                "error": str(e),
                "session_id": session_id,
                "processing_time_ms": elapsed
            }
    
    def _try_learned_query(self, query: str, parsed: Dict) -> Optional[Dict]:
        """Try to find a matching learned query."""
        result = self.learning_system.get_learned_sql(
            question=query,
            entities=parsed.get("entities", {})
        )
        
        if result:
            sql, learned_query = result
            return {
                "sql": sql,
                "template_id": f"LEARNED_{learned_query.id[:8]}",
                "confidence": learned_query.confidence_score
            }
        
        return None
    
    def _try_template_matching(self, parsed: Dict) -> Optional[Dict]:
        """Try to match against SQL templates."""
        template_id, template = self.sql_mapper.map(parsed)
        
        if template_id and template:
            # Get confidence score from mapper
            score = self.sql_mapper.get_match_score(template_id, parsed)
            
            if score >= self.TEMPLATE_CONFIDENCE_THRESHOLD:
                sql = self.sql_mapper.build_query(template_id, template, parsed)
                return {
                    "sql": sql,
                    "template_id": template_id,
                    "template": template,
                    "confidence": score
                }
        
        return None
    
    def _try_dynamic_generation(
        self, query: str, parsed: Dict, language: str
    ) -> Optional[GeneratedQuery]:
        """Try dynamic SQL generation with Claude."""
        try:
            # Get conversation context
            context = None
            if parsed.get("is_followup"):
                context = "This is a follow-up question to previous conversation."
            
            generated = self.dynamic_generator.generate(
                question=query,
                parsed_query=parsed,
                language=language,
                context=context
            )
            
            return generated if generated.is_valid else None
            
        except Exception as e:
            print(f"Dynamic generation error: {e}")
            return None
    
    def _build_response(
        self,
        query: str,
        sql: str,
        parsed: Dict,
        language: str,
        session_id: str,
        source: str,
        template_id: str = None,
        template: Dict = None,
        generated_query: GeneratedQuery = None
    ) -> Dict[str, Any]:
        """Build complete response after getting SQL."""
        start_exec = time.time()
        
        # Check if query is allowed (circuit breaker)
        allowed, reason = self.query_monitor.is_query_allowed(sql)
        if not allowed:
            return {
                "response": f"Query temporarily blocked: {reason}",
                "response_ar": f"الاستعلام محظور مؤقتاً: {reason}",
                "session_id": session_id,
                "source": source,
                "blocked": True
            }
        
        # Execute query with monitoring
        query_id = template_id or f"dynamic_{hashlib.md5(sql.encode()).hexdigest()[:8]}"
        
        with time_query(query_id, sql, source):
            data = self._execute_query(sql)
        
        exec_time = int((time.time() - start_exec) * 1000)
        
        # Use template's chart config if available
        if template and template.get('default_chart'):
            parsed['chart_type'] = template['default_chart']
        elif generated_query and generated_query.chart_suggestion:
            parsed['chart_type'] = generated_query.chart_suggestion
        
        # Generate natural language response
        response = self.response_generator.generate(
            parsed_query=parsed,
            data=data,
            language=language
        )
        
        # Store in context for follow-ups
        self.context_manager.add_turn(
            session_id=session_id,
            user_query=query,
            parsed_query=parsed,
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
            "intent": parsed.get("intent"),
            "entities": parsed.get("entities"),
            "sql": sql,
            "source": source,
            "execution_time_ms": exec_time,
            "cached": False
        }
        
        # Add dynamic generation info
        if generated_query:
            result["generation_info"] = {
                "explanation": generated_query.explanation,
                "confidence": generated_query.confidence,
                "generation_time_ms": generated_query.generation_time_ms
            }
        
        # Cache the result
        self.cache.set(query, language, result)
        
        return result
    
    def _generate_fallback_response(
        self, query: str, parsed: Dict, language: str, session_id: str
    ) -> Dict[str, Any]:
        """Generate a helpful fallback response when query cannot be handled."""
        # Try to suggest relevant tables/columns
        suggested_tables = self.schema_registry.suggest_tables_for_query(query)
        
        if suggested_tables:
            table_info = []
            for table_name in suggested_tables[:3]:
                table = self.schema_registry.get_table(table_name)
                if table:
                    cols = list(table.columns.keys())[:5]
                    table_info.append(f"- {table_name}: {', '.join(cols)}")
            
            suggestion = "\n".join(table_info)
            
            message_en = (
                f"I couldn't find a specific answer for '{query}', but I found some related data:\n\n"
                f"{suggestion}\n\n"
                f"Could you rephrase your question or ask about one of these areas?"
            )
            message_ar = (
                f"لم أتمكن من العثور على إجابة محددة لـ '{query}'، لكنني وجدت بيانات ذات صلة:\n\n"
                f"{suggestion}\n\n"
                f"هل يمكنك إعادة صياغة سؤالك أو السؤال عن أحد هذه المجالات؟"
            )
        else:
            message_en = (
                f"I'm not sure how to answer '{query}'. "
                f"Try asking about inspections, violations, locations, or compliance scores."
            )
            message_ar = (
                f"لست متأكداً كيف أجيب على '{query}'. "
                f"حاول السؤال عن التفتيشات أو المخالفات أو المواقع أو درجات الامتثال."
            )
        
        return {
            "response": message_ar if language == "ar" else message_en,
            "response_en": message_en,
            "response_ar": message_ar,
            "data": [],
            "session_id": session_id,
            "source": "fallback",
            "suggestions": suggested_tables
        }
    
    def _learn_from_query(
        self, query: str, generated: GeneratedQuery, parsed: Dict
    ) -> None:
        """Capture successful dynamic query for learning."""
        try:
            self.learning_system.capture_query(
                question=query,
                sql=generated.sql,
                explanation_en=generated.explanation,
                explanation_ar=generated.explanation_ar,
                intent=parsed.get("intent"),
                entities=parsed.get("entities", {}),
                tables_used=generated.tables_used,
                chart_type=generated.chart_suggestion or "bar",
                execution_time_ms=generated.generation_time_ms,
                success=True
            )
        except Exception as e:
            print(f"Learning capture error: {e}")
    
    def _execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        if not self.db_connection:
            self._connect_db()
        
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(sql)
            
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Query execution error: {e}")
            print(f"SQL: {sql}")
            
            # Record failure for learning
            self.query_monitor.record_execution(
                query_id="error",
                sql=sql,
                execution_time_ms=0,
                success=False,
                error_message=str(e)
            )
            
            return []
    
    # ============== Public API ==============
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        return self.context_manager.get_history(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """Clear session context."""
        self.context_manager.clear_session(session_id)
    
    def get_kpi(self, kpi_id: str, year: int = None) -> Optional[Dict]:
        """Get a KPI value."""
        if self.kpi_library:
            return self.kpi_library.calculate_kpi(kpi_id, year)
        return None
    
    def get_all_kpis(self, year: int = None) -> List[Dict]:
        """Get all KPI values."""
        if self.kpi_library:
            return self.kpi_library.calculate_all_kpis(year)
        return []
    
    def get_template_count(self) -> int:
        """Get number of available templates."""
        return self.sql_mapper.get_template_count()
    
    def get_learned_query_count(self) -> int:
        """Get number of learned queries."""
        return self.learning_system.get_stats()["total_learned_queries"]
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check."""
        return {
            "database": self.db_connection is not None,
            "templates": self.sql_mapper.get_template_count(),
            "learned_queries": self.learning_system.get_stats(),
            "schema_tables": self.schema_registry.stats()["total_tables"],
            "azure_configured": bool(self.azure_endpoint and self.azure_api_key),
            "cache": self.cache.stats(),
            "query_monitor": self.query_monitor.get_stats(),
            "agent_stats": self._stats.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        return {
            "agent_stats": self._stats.copy(),
            "query_monitor": self.query_monitor.get_dashboard_data(),
            "learning_stats": self.learning_system.get_stats(),
            "promotion_candidates": [
                q.to_dict() for q in self.learning_system.get_promotion_candidates()[:5]
            ],
            "cache_stats": self.cache.stats()
        }
    
    def clear_cache(self) -> None:
        """Clear response cache."""
        self.cache.clear()
    
    def close(self) -> None:
        """Close connections."""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None


# Synchronous wrapper
class IntelligentChatAgentSync:
    """Synchronous wrapper for IntelligentChatAgent."""
    
    def __init__(self, *args, **kwargs):
        self._agent = IntelligentChatAgent(*args, **kwargs)
    
    def process_query(
        self,
        query: str,
        session_id: str = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Process query synchronously."""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
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
            return asyncio.run(
                self._agent.process_query(query, session_id, language)
            )
    
    def __getattr__(self, name):
        return getattr(self._agent, name)


# Alias for backward compatibility
InspectionChatAgent = IntelligentChatAgent
InspectionChatAgentSync = IntelligentChatAgentSync
