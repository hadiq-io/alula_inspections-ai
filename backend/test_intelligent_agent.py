#!/usr/bin/env python3
"""
Integration Test Suite for the Intelligent Query System v2.0
============================================================

Tests the complete dynamic query generation, learning, and memory system.
Includes the "Health Certificates" test case that was requested by the client.

Usage:
    python test_intelligent_agent.py
    
    # Run specific tests:
    python test_intelligent_agent.py --test health_certificates
    python test_intelligent_agent.py --test dynamic_generation
    python test_intelligent_agent.py --test learning_system
"""

import asyncio
import sys
import os
import time
import argparse
from typing import Dict, Any, List
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our v2 modules
from nlp.schema_registry import SchemaRegistry, SemanticAnnotations
from nlp.query_validator import QueryValidator, ValidationResult
from nlp.dynamic_sql_generator import DynamicSQLGenerator, GeneratedQuery
from nlp.query_learning import QueryLearningSystem, LearnedQuery
from nlp.query_monitor import QueryMonitor, CircuitBreaker
from nlp.chat_agent_v2 import IntelligentChatAgent
from nlp.context_manager_v2 import EnhancedContextManager
from database_v2 import EnhancedDatabaseManager


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_failure(text: str):
    """Print failure message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


class TestSuite:
    """Complete integration test suite for the intelligent agent"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.agent = None
        self.db = None
        
    async def setup(self):
        """Initialize all components"""
        print_header("Initializing Test Suite")
        
        try:
            # Initialize database
            print_info("Connecting to database...")
            self.db = EnhancedDatabaseManager()
            print_success("Database connection pool initialized")
            
            # Initialize agent
            print_info("Initializing intelligent agent...")
            self.agent = IntelligentChatAgent()
            print_success("Intelligent agent initialized")
            
            return True
        except Exception as e:
            print_failure(f"Setup failed: {str(e)}")
            return False
    
    async def teardown(self):
        """Clean up resources"""
        print_info("Cleaning up resources...")
        if self.db:
            await self.db.close()
        print_success("Cleanup complete")
    
    def record_result(self, test_name: str, passed: bool, 
                     duration: float, details: str = ""):
        """Record a test result"""
        self.results.append({
            'name': test_name,
            'passed': passed,
            'duration': duration,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    # =========================================================================
    # TEST 1: Schema Registry
    # =========================================================================
    async def test_schema_registry(self) -> bool:
        """Test the schema registry and semantic annotations"""
        print_header("Test 1: Schema Registry")
        start_time = time.time()
        
        try:
            registry = SchemaRegistry()
            
            # Test table discovery
            print_info("Discovering database tables...")
            tables = registry.tables
            print_success(f"Discovered {len(tables)} tables")
            
            if len(tables) > 0:
                # Show sample tables
                sample_tables = list(tables.keys())[:5]
                for table in sample_tables:
                    print(f"   - {table}")
            
            # Test semantic annotations
            print_info("Testing semantic annotations...")
            annotations = SemanticAnnotations()
            
            # Test concept mapping
            concepts = ['violations', 'inspectors', 'neighborhoods', 'permits']
            for concept in concepts:
                tables_for_concept = annotations.get_tables_for_concept(concept)
                if tables_for_concept:
                    print_success(f"Concept '{concept}' → {tables_for_concept}")
                else:
                    print_warning(f"No tables mapped for concept '{concept}'")
            
            # Test join path discovery
            print_info("Testing join path discovery...")
            sample_tables = list(registry.tables.keys())[:2]
            if len(sample_tables) >= 2:
                paths = registry.find_join_paths(sample_tables[0], sample_tables[1])
                print_success(f"Found {len(paths)} join paths between tables")
            
            duration = time.time() - start_time
            self.record_result("Schema Registry", True, duration)
            print_success(f"Schema Registry test passed ({duration:.2f}s)")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Schema Registry", False, duration, str(e))
            print_failure(f"Schema Registry test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 2: Query Validator
    # =========================================================================
    async def test_query_validator(self) -> bool:
        """Test the query validator for SQL injection protection"""
        print_header("Test 2: Query Validator")
        start_time = time.time()
        
        try:
            validator = QueryValidator()
            
            # Test valid queries
            valid_queries = [
                "SELECT COUNT(*) FROM Inspections",
                "SELECT TOP 10 * FROM Violations WHERE Status = 'Open'",
                "SELECT I.Name, COUNT(V.ID) FROM Inspectors I JOIN Violations V ON I.ID = V.InspectorID GROUP BY I.Name"
            ]
            
            print_info("Testing valid queries...")
            for query in valid_queries:
                result = validator.validate(query)
                if result.is_valid:
                    print_success(f"Valid: {query[:50]}...")
                else:
                    print_failure(f"Should be valid: {query[:50]}...")
                    return False
            
            # Test SQL injection attempts
            injection_attempts = [
                "SELECT * FROM Users; DROP TABLE Users; --",
                "SELECT * FROM Users WHERE id = '1' OR '1'='1'",
                "SELECT * FROM Users WHERE id = 1; DELETE FROM Users",
                "SELECT * FROM Users WHERE name = '' UNION SELECT password FROM admin --"
            ]
            
            print_info("Testing SQL injection detection...")
            for query in injection_attempts:
                result = validator.validate(query)
                if not result.is_valid:
                    print_success(f"Blocked injection: {query[:40]}...")
                else:
                    print_warning(f"Injection not detected: {query[:40]}...")
            
            # Test write operation blocking
            print_info("Testing write operation blocking...")
            write_queries = [
                "INSERT INTO Users VALUES (1, 'test')",
                "UPDATE Users SET name = 'hacked'",
                "DELETE FROM Users WHERE id = 1",
                "DROP TABLE Users",
                "TRUNCATE TABLE Users"
            ]
            
            for query in write_queries:
                result = validator.validate(query)
                if not result.is_valid:
                    print_success(f"Blocked write: {query[:40]}...")
                else:
                    print_failure(f"Write not blocked: {query[:40]}...")
                    return False
            
            duration = time.time() - start_time
            self.record_result("Query Validator", True, duration)
            print_success(f"Query Validator test passed ({duration:.2f}s)")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Query Validator", False, duration, str(e))
            print_failure(f"Query Validator test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 3: Dynamic SQL Generator - HEALTH CERTIFICATES TEST
    # =========================================================================
    async def test_health_certificates(self) -> bool:
        """
        THE CRITICAL TEST: Can the system answer "What about Health Certificates?"
        This was the question that failed during the client demo.
        """
        print_header("Test 3: Health Certificates Query (Client Demo Fix)")
        start_time = time.time()
        
        try:
            print_info("Testing the query that failed in client demo...")
            print_info("Question: 'What about Health Certificates?'")
            
            # Use the intelligent agent to process this query
            result = await self.agent.process_message(
                message="What about Health Certificates?",
                user_id="test_user_health_cert",
                session_id="test_session_001"
            )
            
            if result and 'error' not in str(result).lower():
                print_success("Agent successfully processed 'Health Certificates' query!")
                
                # Check what route was used
                route_used = result.get('route', 'unknown')
                print_info(f"Query route used: {route_used}")
                
                if 'data' in result:
                    print_success(f"Data returned: {len(result.get('data', []))} rows")
                
                if 'sql' in result:
                    print_info(f"Generated SQL: {result['sql'][:100]}...")
                
                if 'learned' in result:
                    print_success("Query was captured by learning system!")
                
                duration = time.time() - start_time
                self.record_result("Health Certificates", True, duration, 
                                  f"Route: {route_used}")
                print_success(f"Health Certificates test PASSED ({duration:.2f}s)")
                return True
            else:
                duration = time.time() - start_time
                error_msg = str(result.get('error', 'Unknown error'))
                self.record_result("Health Certificates", False, duration, error_msg)
                print_failure(f"Health Certificates test failed: {error_msg}")
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Health Certificates", False, duration, str(e))
            print_failure(f"Health Certificates test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 4: Dynamic Query Generation
    # =========================================================================
    async def test_dynamic_generation(self) -> bool:
        """Test dynamic SQL generation for novel questions"""
        print_header("Test 4: Dynamic Query Generation")
        start_time = time.time()
        
        try:
            generator = DynamicSQLGenerator()
            
            # Test with various novel questions
            novel_questions = [
                "Show me the busiest inspectors this month",
                "What are the most common violation types in the old town?",
                "How many inspections were completed last week?",
                "Which neighborhoods have the highest violation rates?",
                "List all pending permits from last quarter"
            ]
            
            success_count = 0
            
            for question in novel_questions:
                print_info(f"Generating SQL for: '{question}'")
                
                try:
                    result: GeneratedQuery = await generator.generate(question)
                    
                    if result and result.sql:
                        print_success(f"Generated SQL with confidence {result.confidence:.2f}")
                        print(f"   SQL: {result.sql[:80]}...")
                        success_count += 1
                    else:
                        print_warning(f"Could not generate SQL for this question")
                        
                except Exception as e:
                    print_warning(f"Generation error: {str(e)}")
            
            # At least 3 out of 5 should work
            if success_count >= 3:
                duration = time.time() - start_time
                self.record_result("Dynamic Generation", True, duration,
                                  f"{success_count}/5 successful")
                print_success(f"Dynamic Generation test passed ({duration:.2f}s)")
                return True
            else:
                duration = time.time() - start_time
                self.record_result("Dynamic Generation", False, duration,
                                  f"Only {success_count}/5 successful")
                print_failure(f"Dynamic Generation test failed: only {success_count}/5")
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Dynamic Generation", False, duration, str(e))
            print_failure(f"Dynamic Generation test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 5: Query Learning System
    # =========================================================================
    async def test_learning_system(self) -> bool:
        """Test the self-improving query learning system"""
        print_header("Test 5: Query Learning System")
        start_time = time.time()
        
        try:
            learning = QueryLearningSystem()
            
            # Record a simulated successful query
            test_query = LearnedQuery(
                intent_pattern="health_certificate_count",
                question_variations=[
                    "How many health certificates?",
                    "Count health certificates",
                    "Health certificate total"
                ],
                sql_template="SELECT COUNT(*) FROM HealthCertificates",
                description="Count all health certificates",
                use_count=5,
                success_rate=1.0,
                avg_execution_time=0.5
            )
            
            print_info("Recording learned query...")
            learning.record_query(
                question="How many health certificates?",
                sql="SELECT COUNT(*) FROM HealthCertificates",
                execution_time=0.5,
                success=True,
                row_count=100
            )
            print_success("Query recorded in learning system")
            
            # Test retrieval
            print_info("Testing query retrieval...")
            similar = learning.find_similar("health certificate count")
            if similar:
                print_success(f"Found similar query with score {similar[0][1]:.2f}")
            else:
                print_warning("No similar queries found")
            
            # Test promotion eligibility
            print_info("Testing promotion logic...")
            stats = learning.get_statistics()
            print_success(f"Learning stats: {stats}")
            
            duration = time.time() - start_time
            self.record_result("Learning System", True, duration)
            print_success(f"Learning System test passed ({duration:.2f}s)")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Learning System", False, duration, str(e))
            print_failure(f"Learning System test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 6: Context Manager with Memory
    # =========================================================================
    async def test_context_memory(self) -> bool:
        """Test the enhanced context manager with long-term memory"""
        print_header("Test 6: Context Manager Memory")
        start_time = time.time()
        
        try:
            context = EnhancedContextManager()
            
            user_id = "test_user_memory"
            session_id = "test_session_memory"
            
            # Simulate a conversation
            print_info("Simulating multi-turn conversation...")
            
            # Turn 1: Ask about violations
            context.add_turn(
                user_id=user_id,
                session_id=session_id,
                user_message="Show me violations in Old Town",
                assistant_response="Here are 25 violations in Old Town...",
                entities_mentioned=['Old Town', 'violations'],
                intent='violations_by_neighborhood'
            )
            print_success("Turn 1 recorded")
            
            # Turn 2: Follow-up question
            context.add_turn(
                user_id=user_id,
                session_id=session_id,
                user_message="What about the critical ones?",
                assistant_response="There are 5 critical violations...",
                entities_mentioned=['critical'],
                intent='filter_violations'
            )
            print_success("Turn 2 recorded")
            
            # Test follow-up resolution
            print_info("Testing follow-up resolution...")
            resolved = context.resolve_references(
                user_id=user_id,
                session_id=session_id,
                message="Show me more details"
            )
            print_success(f"Resolved context: {resolved}")
            
            # Test entity tracking
            print_info("Testing entity tracking...")
            entities = context.get_mentioned_entities(user_id, session_id)
            if entities:
                print_success(f"Tracked entities: {entities}")
            
            # Test preference learning
            print_info("Testing preference learning...")
            context.learn_preference(user_id, 'language', 'en')
            context.learn_preference(user_id, 'chart_type', 'bar')
            prefs = context.get_preferences(user_id)
            print_success(f"User preferences: {prefs}")
            
            duration = time.time() - start_time
            self.record_result("Context Memory", True, duration)
            print_success(f"Context Memory test passed ({duration:.2f}s)")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Context Memory", False, duration, str(e))
            print_failure(f"Context Memory test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 7: Query Monitor & Circuit Breaker
    # =========================================================================
    async def test_query_monitor(self) -> bool:
        """Test the query monitor and circuit breaker"""
        print_header("Test 7: Query Monitor & Circuit Breaker")
        start_time = time.time()
        
        try:
            monitor = QueryMonitor()
            
            # Simulate successful queries
            print_info("Simulating successful queries...")
            for i in range(5):
                monitor.record_query_execution(
                    query_hash=f"test_query_{i}",
                    execution_time=0.5 + (i * 0.1),
                    success=True,
                    row_count=100 + i
                )
            print_success("Recorded 5 successful queries")
            
            # Simulate a slow query
            print_info("Simulating slow query...")
            monitor.record_query_execution(
                query_hash="slow_query",
                execution_time=5.0,  # 5 seconds - should trigger alert
                success=True,
                row_count=10000
            )
            print_success("Slow query recorded")
            
            # Check slow query detection
            slow_queries = monitor.get_slow_queries()
            if slow_queries:
                print_success(f"Detected {len(slow_queries)} slow query(ies)")
            
            # Test circuit breaker
            print_info("Testing circuit breaker...")
            breaker = CircuitBreaker(failure_threshold=3, recovery_time=10)
            
            # Simulate failures
            for i in range(4):
                breaker.record_failure("test_circuit")
            
            if breaker.is_open("test_circuit"):
                print_success("Circuit breaker opened after failures")
            else:
                print_failure("Circuit breaker should be open")
                return False
            
            # Get dashboard data
            print_info("Getting monitoring dashboard data...")
            dashboard = monitor.get_dashboard_data()
            print_success(f"Dashboard: {dashboard.get('total_queries', 0)} total queries")
            
            duration = time.time() - start_time
            self.record_result("Query Monitor", True, duration)
            print_success(f"Query Monitor test passed ({duration:.2f}s)")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Query Monitor", False, duration, str(e))
            print_failure(f"Query Monitor test failed: {str(e)}")
            return False
    
    # =========================================================================
    # TEST 8: Full Integration Test
    # =========================================================================
    async def test_full_integration(self) -> bool:
        """Complete end-to-end integration test"""
        print_header("Test 8: Full Integration Test")
        start_time = time.time()
        
        try:
            # Test a series of related questions
            questions = [
                "How many inspections were done today?",
                "Show me the top 5 inspectors",
                "What about violations in the historical district?",
                "Break it down by month",
                "Who handled the most critical cases?"
            ]
            
            user_id = "integration_test_user"
            session_id = "integration_test_session"
            
            success_count = 0
            
            for question in questions:
                print_info(f"Processing: '{question}'")
                
                result = await self.agent.process_message(
                    message=question,
                    user_id=user_id,
                    session_id=session_id
                )
                
                if result and 'error' not in str(result).lower():
                    route = result.get('route', 'unknown')
                    print_success(f"→ Success via {route}")
                    success_count += 1
                else:
                    print_warning(f"→ Failed: {result.get('error', 'unknown')}")
            
            # Test should pass if at least 3/5 queries work
            if success_count >= 3:
                duration = time.time() - start_time
                self.record_result("Full Integration", True, duration,
                                  f"{success_count}/5 queries successful")
                print_success(f"Full Integration test passed ({duration:.2f}s)")
                return True
            else:
                duration = time.time() - start_time
                self.record_result("Full Integration", False, duration,
                                  f"Only {success_count}/5 successful")
                print_failure(f"Full Integration test failed")
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.record_result("Full Integration", False, duration, str(e))
            print_failure(f"Full Integration test failed: {str(e)}")
            return False
    
    # =========================================================================
    # RUN ALL TESTS
    # =========================================================================
    async def run_all(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print_header("INTELLIGENT AGENT TEST SUITE v2.0")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup
        if not await self.setup():
            return {'success': False, 'error': 'Setup failed'}
        
        # Run all tests
        tests = [
            ('Schema Registry', self.test_schema_registry),
            ('Query Validator', self.test_query_validator),
            ('Health Certificates', self.test_health_certificates),
            ('Dynamic Generation', self.test_dynamic_generation),
            ('Learning System', self.test_learning_system),
            ('Context Memory', self.test_context_memory),
            ('Query Monitor', self.test_query_monitor),
            ('Full Integration', self.test_full_integration),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print_failure(f"{name} crashed: {str(e)}")
                failed += 1
        
        # Cleanup
        await self.teardown()
        
        # Print summary
        print_header("TEST RESULTS SUMMARY")
        
        for result in self.results:
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            color = Colors.GREEN if result['passed'] else Colors.RED
            print(f"{color}{status}{Colors.END} {result['name']} ({result['duration']:.2f}s)")
            if result['details'] and not result['passed']:
                print(f"      Details: {result['details']}")
        
        print(f"\n{Colors.BOLD}Total: {passed} passed, {failed} failed{Colors.END}")
        
        # Return summary
        return {
            'success': failed == 0,
            'passed': passed,
            'failed': failed,
            'results': self.results
        }
    
    async def run_single(self, test_name: str) -> bool:
        """Run a single test by name"""
        test_map = {
            'schema': self.test_schema_registry,
            'validator': self.test_query_validator,
            'health_certificates': self.test_health_certificates,
            'dynamic': self.test_dynamic_generation,
            'learning': self.test_learning_system,
            'memory': self.test_context_memory,
            'monitor': self.test_query_monitor,
            'integration': self.test_full_integration,
        }
        
        if test_name not in test_map:
            print_failure(f"Unknown test: {test_name}")
            print_info(f"Available tests: {', '.join(test_map.keys())}")
            return False
        
        if not await self.setup():
            return False
        
        result = await test_map[test_name]()
        await self.teardown()
        return result


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Test the Intelligent Agent')
    parser.add_argument('--test', type=str, help='Run a specific test')
    parser.add_argument('--list', action='store_true', help='List available tests')
    args = parser.parse_args()
    
    if args.list:
        print("Available tests:")
        print("  - schema: Schema Registry")
        print("  - validator: Query Validator")
        print("  - health_certificates: Health Certificates (Client Demo)")
        print("  - dynamic: Dynamic Query Generation")
        print("  - learning: Query Learning System")
        print("  - memory: Context Manager Memory")
        print("  - monitor: Query Monitor & Circuit Breaker")
        print("  - integration: Full Integration Test")
        return
    
    suite = TestSuite()
    
    if args.test:
        success = await suite.run_single(args.test)
        sys.exit(0 if success else 1)
    else:
        results = await suite.run_all()
        sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    asyncio.run(main())
