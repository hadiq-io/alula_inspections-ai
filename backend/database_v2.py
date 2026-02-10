"""
Database Module - Enhanced with Connection Pooling and Multi-Tier Caching
==========================================================================
High-performance database layer with connection pooling, intelligent caching,
and async support for optimal query execution.

Features:
- Connection pooling (min 5, max 20 connections)
- Multi-tier caching (L1: memory, L2: disk for expensive queries)
- Async query execution support
- Query performance tracking
- Automatic retry with exponential backoff
- Health monitoring integration

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import time
import json
import hashlib
import threading
import pickle
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
from collections import OrderedDict
import pyodbc
import pandas as pd
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, Future

load_dotenv()


class LRUCache:
    """Thread-safe LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items
            ttl_seconds: Time-to-live in seconds
        """
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check TTL
            if time.time() - self._timestamps[key] > self._ttl:
                del self._cache[key]
                del self._timestamps[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._max_size:
                    # Remove oldest item
                    oldest = next(iter(self._cache))
                    del self._cache[oldest]
                    del self._timestamps[oldest]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._hits = 0
            self._misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total, 3) if total > 0 else 0
            }


class DiskCache:
    """Disk-based cache for expensive query results."""
    
    def __init__(self, cache_dir: str = None, ttl_seconds: int = 3600):
        """
        Initialize disk cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl_seconds: Time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = str(Path(__file__).parent / ".cache")
        
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
    
    def _get_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        return self._cache_dir / f"{key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from disk cache."""
        path = self._get_path(key)
        
        if not path.exists():
            return None
        
        try:
            # Check TTL via file modification time
            mtime = path.stat().st_mtime
            if time.time() - mtime > self._ttl:
                path.unlink()
                return None
            
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in disk cache."""
        path = self._get_path(key)
        
        try:
            with self._lock:
                with open(path, 'wb') as f:
                    pickle.dump(value, f)
        except Exception as e:
            print(f"Disk cache write error: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete item from disk cache."""
        path = self._get_path(key)
        
        if path.exists():
            path.unlink()
            return True
        return False
    
    def clear(self) -> int:
        """Clear all cached items. Returns count deleted."""
        count = 0
        for path in self._cache_dir.glob("*.cache"):
            path.unlink()
            count += 1
        return count
    
    def cleanup_expired(self) -> int:
        """Remove expired cache files."""
        count = 0
        now = time.time()
        
        for path in self._cache_dir.glob("*.cache"):
            if now - path.stat().st_mtime > self._ttl:
                path.unlink()
                count += 1
        
        return count


class ConnectionPool:
    """Thread-safe connection pool for SQL Server."""
    
    def __init__(
        self,
        connection_string: str,
        min_connections: int = 5,
        max_connections: int = 20,
        timeout: int = 30
    ):
        """
        Initialize connection pool.
        
        Args:
            connection_string: ODBC connection string
            min_connections: Minimum connections to maintain
            max_connections: Maximum connections allowed
            timeout: Connection timeout in seconds
        """
        self._connection_string = connection_string
        self._min_connections = min_connections
        self._max_connections = max_connections
        self._timeout = timeout
        
        self._pool: List[pyodbc.Connection] = []
        self._in_use: Dict[int, pyodbc.Connection] = {}
        self._lock = threading.RLock()
        self._semaphore = threading.Semaphore(max_connections)
        
        # Statistics
        self._created = 0
        self._acquired = 0
        self._released = 0
        self._errors = 0
        
        # Pre-warm pool
        self._warm_pool()
    
    def _warm_pool(self) -> None:
        """Pre-create minimum connections."""
        for _ in range(self._min_connections):
            try:
                conn = self._create_connection()
                self._pool.append(conn)
            except Exception as e:
                print(f"Pool warm-up error: {e}")
                break
    
    def _create_connection(self) -> pyodbc.Connection:
        """Create a new database connection."""
        conn = pyodbc.connect(self._connection_string, timeout=self._timeout)
        self._created += 1
        return conn
    
    def _is_connection_valid(self, conn: pyodbc.Connection) -> bool:
        """Check if connection is still valid."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
    
    def acquire(self) -> pyodbc.Connection:
        """Acquire a connection from the pool."""
        self._semaphore.acquire()
        
        with self._lock:
            while self._pool:
                conn = self._pool.pop()
                
                if self._is_connection_valid(conn):
                    self._in_use[id(conn)] = conn
                    self._acquired += 1
                    return conn
                else:
                    # Connection is dead, close it
                    try:
                        conn.close()
                    except Exception:
                        pass
            
            # No available connections, create new one
            try:
                conn = self._create_connection()
                self._in_use[id(conn)] = conn
                self._acquired += 1
                return conn
            except Exception as e:
                self._errors += 1
                self._semaphore.release()
                raise
    
    def release(self, conn: pyodbc.Connection) -> None:
        """Release a connection back to the pool."""
        with self._lock:
            conn_id = id(conn)
            
            if conn_id in self._in_use:
                del self._in_use[conn_id]
            
            # Return to pool if valid and not at max
            if len(self._pool) < self._max_connections:
                if self._is_connection_valid(conn):
                    self._pool.append(conn)
                else:
                    try:
                        conn.close()
                    except Exception:
                        pass
            else:
                try:
                    conn.close()
                except Exception:
                    pass
            
            self._released += 1
        
        self._semaphore.release()
    
    def close_all(self) -> None:
        """Close all connections."""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            
            for conn in self._in_use.values():
                try:
                    conn.close()
                except Exception:
                    pass
            
            self._pool.clear()
            self._in_use.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self._lock:
            return {
                "pool_size": len(self._pool),
                "in_use": len(self._in_use),
                "total_created": self._created,
                "total_acquired": self._acquired,
                "total_released": self._released,
                "errors": self._errors,
                "max_connections": self._max_connections
            }
    
    def __enter__(self):
        return self.acquire()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Note: Connection should be released manually
        pass


class Database:
    """
    Enhanced database class with connection pooling and multi-tier caching.
    
    Features:
    - Connection pooling for efficient resource usage
    - L1 memory cache for frequent queries (5 min TTL)
    - L2 disk cache for expensive queries (1 hour TTL)
    - Async query execution support
    - Automatic retry with exponential backoff
    - Query performance tracking
    """
    
    def __init__(self):
        """Initialize database with connection pool and caches."""
        self.server = os.getenv('DB_SERVER', '20.3.236.169')
        self.port = int(os.getenv('DB_PORT', '1433'))
        self.database = os.getenv('DB_NAME', 'CHECK_ELM_AlUlaRC_DW')
        self.username = os.getenv('DB_USERNAME', 'sa')
        self.password = os.getenv('DB_PASSWORD', 'StrongPass123!')
        
        # Build connection string
        self._connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        # Initialize connection pool
        self._pool = ConnectionPool(
            self._connection_string,
            min_connections=5,
            max_connections=20,
            timeout=30
        )
        
        # Initialize caches
        self._l1_cache = LRUCache(max_size=200, ttl_seconds=300)  # 5 minutes
        self._l2_cache = DiskCache(ttl_seconds=3600)  # 1 hour
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # Query statistics
        self._stats = {
            "total_queries": 0,
            "cache_hits_l1": 0,
            "cache_hits_l2": 0,
            "cache_misses": 0,
            "total_time_ms": 0.0
        }
        self._stats_lock = threading.Lock()
    
    def _make_cache_key(self, query: str) -> str:
        """Create a cache key from query."""
        # Normalize query
        normalized = ' '.join(query.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]
    
    def get_connection(self) -> pyodbc.Connection:
        """Get a connection from the pool."""
        return self._pool.acquire()
    
    def release_connection(self, conn: pyodbc.Connection) -> None:
        """Release a connection back to the pool."""
        self._pool.release(conn)
    
    def execute_query(
        self,
        query: str,
        use_cache: bool = True,
        cache_tier: str = "l1",  # "l1", "l2", or "both"
        max_retries: int = 3
    ) -> pd.DataFrame:
        """
        Execute a SQL query with caching and retry logic.
        
        Args:
            query: SQL query to execute
            use_cache: Whether to use caching
            cache_tier: Which cache tier(s) to use
            max_retries: Maximum retry attempts
            
        Returns:
            Query results as DataFrame
        """
        start_time = time.time()
        cache_key = self._make_cache_key(query)
        
        # Check L1 cache
        if use_cache and cache_tier in ("l1", "both"):
            cached = self._l1_cache.get(cache_key)
            if cached is not None:
                with self._stats_lock:
                    self._stats["cache_hits_l1"] += 1
                return cached
        
        # Check L2 cache
        if use_cache and cache_tier in ("l2", "both"):
            cached = self._l2_cache.get(cache_key)
            if cached is not None:
                with self._stats_lock:
                    self._stats["cache_hits_l2"] += 1
                # Promote to L1
                self._l1_cache.set(cache_key, cached)
                return cached
        
        # Execute query with retries
        last_error = None
        for attempt in range(max_retries):
            conn = None
            try:
                conn = self._pool.acquire()
                df = pd.read_sql(query, conn)
                
                # Update stats
                elapsed = (time.time() - start_time) * 1000
                with self._stats_lock:
                    self._stats["total_queries"] += 1
                    self._stats["cache_misses"] += 1
                    self._stats["total_time_ms"] += elapsed
                
                # Cache the result
                if use_cache:
                    self._l1_cache.set(cache_key, df)
                    if cache_tier in ("l2", "both"):
                        self._l2_cache.set(cache_key, df)
                
                return df
                
            except Exception as e:
                last_error = e
                print(f"Query attempt {attempt + 1} failed: {e}")
                
                # Exponential backoff
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (2 ** attempt))
            finally:
                if conn:
                    self._pool.release(conn)
        
        print(f"❌ Query failed after {max_retries} attempts: {last_error}")
        return pd.DataFrame()
    
    def execute_query_async(
        self,
        query: str,
        use_cache: bool = True
    ) -> Future:
        """
        Execute a query asynchronously.
        
        Args:
            query: SQL query to execute
            use_cache: Whether to use caching
            
        Returns:
            Future that resolves to DataFrame
        """
        return self._executor.submit(self.execute_query, query, use_cache)
    
    def execute_raw(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a raw query and return results as list of dicts.
        Does not use caching.
        """
        conn = None
        try:
            conn = self._pool.acquire()
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            return results
            
        except Exception as e:
            print(f"❌ Raw query error: {e}")
            return []
        finally:
            if conn:
                self._pool.release(conn)
    
    def execute_scalar(self, query: str) -> Optional[Any]:
        """Execute a query and return single value."""
        conn = None
        try:
            conn = self._pool.acquire()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Scalar query error: {e}")
            return None
        finally:
            if conn:
                self._pool.release(conn)
    
    # ============== Existing Methods (Updated) ==============
    
    def get_ml_summary(self) -> pd.DataFrame:
        """Get summary of all 9 ML models."""
        query = """
        SELECT 
            'KPI_01 & KPI_02' AS Model,
            'ML_Predictions' AS TableName,
            COUNT(*) AS RecordCount,
            MAX(generated_at) AS LastUpdated
        FROM ML_Predictions
        UNION ALL
        SELECT 'KPI_03', 'ML_Location_Risk', COUNT(*), MAX(generated_at) FROM ML_Location_Risk
        UNION ALL
        SELECT 'KPI_04', 'ML_Anomalies', COUNT(*), MAX(detected_at) FROM ML_Anomalies
        UNION ALL
        SELECT 'KPI_05', 'ML_Severity_Predictions', COUNT(*), MAX(predicted_at) FROM ML_Severity_Predictions
        UNION ALL
        SELECT 'KPI_06', 'ML_Scheduling_Recommendations', COUNT(*), MAX(generated_at) FROM ML_Scheduling_Recommendations
        UNION ALL
        SELECT 'KPI_07', 'ML_Objection_Predictions', COUNT(*), MAX(predicted_at) FROM ML_Objection_Predictions
        UNION ALL
        SELECT 'KPI_08', 'ML_Location_Clusters', COUNT(*), MAX(generated_at) FROM ML_Location_Clusters
        UNION ALL
        SELECT 'KPI_09', 'ML_Recurrence_Predictions', COUNT(*), MAX(predicted_at) FROM ML_Recurrence_Predictions
        UNION ALL
        SELECT 'KPI_10', 'ML_Inspector_Performance', COUNT(*), MAX(classified_at) FROM ML_Inspector_Performance
        ORDER BY Model
        """
        return self.execute_query(query, cache_tier="l2")  # Long-lived cache
    
    def get_high_risk_locations(self, limit: int = 20) -> pd.DataFrame:
        """Get high-risk locations."""
        query = f"""
        SELECT TOP {limit}
            mlr.location_id, 
            COALESCE(l.Name, 'Unknown Location ID: ' + CAST(mlr.location_id AS VARCHAR)) as location_name,
            COALESCE(l.NameAr, l.Name, 'موقع غير معروف') as location_name_ar,
            mlr.risk_probability, 
            mlr.risk_category,
            mlr.total_violations, 
            mlr.critical_violations,
            mlr.last_inspection_score, 
            mlr.days_since_inspection
        FROM ML_Location_Risk mlr
        LEFT JOIN Locations l ON mlr.location_id = l.Id
        ORDER BY mlr.risk_probability DESC
        """
        return self.execute_query(query)
    
    def get_inspector_performance(self) -> pd.DataFrame:
        """Get inspector performance data."""
        query = """
        SELECT 
            inspector_id, total_inspections, avg_inspection_score,
            completion_rate, performance_score, predicted_label
        FROM ML_Inspector_Performance
        ORDER BY performance_score DESC
        """
        return self.execute_query(query)
    
    def get_anomalies(self, limit: int = 20) -> pd.DataFrame:
        """Get anomaly detections."""
        query = f"""
        SELECT TOP {limit}
            inspection_id, location_id, anomaly_probability,
            anomaly_type, score, duration_minutes, total_issues
        FROM ML_Anomalies
        ORDER BY anomaly_probability DESC
        """
        return self.execute_query(query)
    
    def get_recurrence_predictions(self, limit: int = 20) -> pd.DataFrame:
        """Get recurrence predictions."""
        query = f"""
        SELECT TOP {limit}
            question_id, event_id, location_id, severity,
            recurrence_probability, predicted_recurrence, actual_recurrence
        FROM ML_Recurrence_Predictions
        ORDER BY recurrence_probability DESC
        """
        return self.execute_query(query)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        try:
            # Use parallel queries for better performance
            futures = [
                self.execute_query_async("SELECT COUNT(*) as cnt FROM Event WHERE IsDeleted = 0"),
                self.execute_query_async("SELECT AVG(CAST(Score AS FLOAT)) as avg FROM Event WHERE IsDeleted = 0"),
                self.execute_query_async("SELECT COUNT(*) as cnt FROM ML_Location_Risk WHERE risk_probability > 70")
            ]
            
            results = [f.result() for f in futures]
            
            return {
                "total_inspections": int(results[0]['cnt'].iloc[0]) if not results[0].empty else 0,
                "avg_compliance_score": round(float(results[1]['avg'].iloc[0]), 2) if not results[1].empty else 0,
                "high_risk_locations": int(results[2]['cnt'].iloc[0]) if not results[2].empty else 0,
                "active_ml_models": 9
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                "total_inspections": 0,
                "avg_compliance_score": 0,
                "high_risk_locations": 0,
                "active_ml_models": 9
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            start = time.time()
            result = self.execute_scalar("SELECT 1")
            latency = (time.time() - start) * 1000
            
            return {
                "status": "healthy" if result == 1 else "degraded",
                "latency_ms": round(latency, 2),
                "pool_stats": self._pool.stats(),
                "l1_cache": self._l1_cache.stats(),
                "query_stats": self._stats.copy()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "pool_stats": self._pool.stats()
            }
    
    def clear_cache(self, tier: str = "all") -> Dict[str, int]:
        """Clear cache(s)."""
        result = {}
        
        if tier in ("l1", "all"):
            self._l1_cache.clear()
            result["l1_cleared"] = True
        
        if tier in ("l2", "all"):
            result["l2_files_deleted"] = self._l2_cache.clear()
        
        return result
    
    def stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        with self._stats_lock:
            stats = self._stats.copy()
        
        if stats["total_queries"] > 0:
            stats["avg_query_time_ms"] = round(
                stats["total_time_ms"] / stats["total_queries"], 2
            )
            total_hits = stats["cache_hits_l1"] + stats["cache_hits_l2"]
            total_requests = total_hits + stats["cache_misses"]
            stats["cache_hit_rate"] = round(
                total_hits / total_requests, 3
            ) if total_requests > 0 else 0
        else:
            stats["avg_query_time_ms"] = 0
            stats["cache_hit_rate"] = 0
        
        stats["pool"] = self._pool.stats()
        stats["l1_cache"] = self._l1_cache.stats()
        
        return stats
    
    def close(self) -> None:
        """Close all connections and cleanup."""
        self._pool.close_all()
        self._executor.shutdown(wait=False)


# Singleton instance
_database: Optional[Database] = None
_db_lock = threading.Lock()


def get_database() -> Database:
    """Get the global database instance."""
    global _database
    
    with _db_lock:
        if _database is None:
            _database = Database()
        return _database
