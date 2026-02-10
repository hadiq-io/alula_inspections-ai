"""
Query Monitor - Performance Tracking and Health Monitoring
==========================================================
Tracks query execution performance, monitors for issues,
and provides automatic rollback of problematic queries.

Features:
- Real-time query performance tracking
- Slow query detection and alerting
- Failure rate monitoring
- Automatic circuit breaker for bad queries
- Query execution statistics
- Health dashboard data

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import time
import threading
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import statistics


class QueryStatus(Enum):
    """Query execution status."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class QueryExecution:
    """Record of a single query execution."""
    query_id: str
    sql_hash: str
    execution_time_ms: float
    status: QueryStatus
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    rows_returned: int = 0
    source: str = "template"  # "template" or "dynamic"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "sql_hash": self.sql_hash,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message,
            "rows_returned": self.rows_returned,
            "source": self.source
        }


@dataclass
class QueryHealth:
    """Health status for a specific query."""
    sql_hash: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    last_execution: Optional[datetime] = None
    is_circuit_open: bool = False  # If True, query is blocked
    circuit_opened_at: Optional[datetime] = None
    consecutive_failures: int = 0
    
    @property
    def avg_time_ms(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.total_time_ms / self.total_executions
    
    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    @property
    def failure_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.failed_executions / self.total_executions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sql_hash": self.sql_hash,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "avg_time_ms": round(self.avg_time_ms, 2),
            "min_time_ms": round(self.min_time_ms, 2) if self.min_time_ms != float('inf') else 0,
            "max_time_ms": round(self.max_time_ms, 2),
            "success_rate": round(self.success_rate, 3),
            "is_circuit_open": self.is_circuit_open,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None
        }


class CircuitBreaker:
    """
    Circuit breaker pattern for query protection.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Query blocked after failures
    - HALF_OPEN: Testing if query recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)
        self.success_threshold = success_threshold
        
        self._failures: Dict[str, int] = {}
        self._opened_at: Dict[str, datetime] = {}
        self._half_open_successes: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def is_open(self, sql_hash: str) -> bool:
        """Check if circuit is open for a query."""
        with self._lock:
            if sql_hash not in self._opened_at:
                return False
            
            # Check if recovery timeout passed
            if datetime.now() - self._opened_at[sql_hash] > self.recovery_timeout:
                # Move to half-open
                return False
            
            return True
    
    def record_success(self, sql_hash: str) -> None:
        """Record a successful execution."""
        with self._lock:
            self._failures[sql_hash] = 0
            
            if sql_hash in self._opened_at:
                # In half-open state
                self._half_open_successes[sql_hash] = self._half_open_successes.get(sql_hash, 0) + 1
                
                if self._half_open_successes[sql_hash] >= self.success_threshold:
                    # Close the circuit
                    del self._opened_at[sql_hash]
                    del self._half_open_successes[sql_hash]
    
    def record_failure(self, sql_hash: str) -> bool:
        """
        Record a failed execution.
        Returns True if circuit was opened.
        """
        with self._lock:
            self._failures[sql_hash] = self._failures.get(sql_hash, 0) + 1
            
            # Reset half-open tracking
            if sql_hash in self._half_open_successes:
                del self._half_open_successes[sql_hash]
            
            if self._failures[sql_hash] >= self.failure_threshold:
                self._opened_at[sql_hash] = datetime.now()
                return True
            
            return False
    
    def reset(self, sql_hash: str) -> None:
        """Reset circuit for a query."""
        with self._lock:
            self._failures.pop(sql_hash, None)
            self._opened_at.pop(sql_hash, None)
            self._half_open_successes.pop(sql_hash, None)


class QueryMonitor:
    """
    Central monitoring system for query execution.
    
    Features:
    - Track all query executions
    - Detect slow queries
    - Monitor failure rates
    - Circuit breaker for protection
    - Real-time statistics
    - Alerting hooks
    """
    
    # Thresholds
    SLOW_QUERY_THRESHOLD_MS = 3000  # 3 seconds
    VERY_SLOW_QUERY_THRESHOLD_MS = 10000  # 10 seconds
    HIGH_FAILURE_RATE_THRESHOLD = 0.3  # 30% failure rate
    
    # History settings
    MAX_HISTORY_SIZE = 1000
    STATS_WINDOW_HOURS = 24
    
    def __init__(self):
        """Initialize the query monitor."""
        self._lock = threading.Lock()
        
        # Recent execution history (ring buffer)
        self._history: deque = deque(maxlen=self.MAX_HISTORY_SIZE)
        
        # Per-query health tracking
        self._query_health: Dict[str, QueryHealth] = {}
        
        # Circuit breaker
        self._circuit_breaker = CircuitBreaker()
        
        # Alert callbacks
        self._alert_callbacks: List[Callable] = []
        
        # Aggregate statistics
        self._stats = {
            "total_queries": 0,
            "total_successes": 0,
            "total_failures": 0,
            "total_time_ms": 0.0,
            "slow_queries": 0,
            "dynamic_queries": 0,
            "template_queries": 0
        }
        
        # Recent slow queries for debugging
        self._slow_queries: deque = deque(maxlen=50)
        
        # Recent errors for debugging
        self._recent_errors: deque = deque(maxlen=50)
    
    def record_execution(
        self,
        query_id: str,
        sql: str,
        execution_time_ms: float,
        success: bool,
        error_message: str = None,
        rows_returned: int = 0,
        source: str = "template"
    ) -> None:
        """
        Record a query execution.
        
        Args:
            query_id: Unique identifier for the query
            sql: The SQL that was executed
            execution_time_ms: Execution time in milliseconds
            success: Whether execution succeeded
            error_message: Error message if failed
            rows_returned: Number of rows returned
            source: "template" or "dynamic"
        """
        import hashlib
        sql_hash = hashlib.md5(sql.encode()).hexdigest()[:16]
        
        status = QueryStatus.SUCCESS if success else QueryStatus.FAILURE
        
        execution = QueryExecution(
            query_id=query_id,
            sql_hash=sql_hash,
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message,
            rows_returned=rows_returned,
            source=source
        )
        
        with self._lock:
            # Add to history
            self._history.append(execution)
            
            # Update aggregate stats
            self._stats["total_queries"] += 1
            self._stats["total_time_ms"] += execution_time_ms
            
            if source == "dynamic":
                self._stats["dynamic_queries"] += 1
            else:
                self._stats["template_queries"] += 1
            
            if success:
                self._stats["total_successes"] += 1
                self._circuit_breaker.record_success(sql_hash)
            else:
                self._stats["total_failures"] += 1
                circuit_opened = self._circuit_breaker.record_failure(sql_hash)
                
                # Store recent error
                self._recent_errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "query_id": query_id,
                    "error": error_message,
                    "sql_hash": sql_hash
                })
                
                if circuit_opened:
                    self._trigger_alert(
                        "circuit_opened",
                        f"Circuit breaker opened for query {sql_hash}"
                    )
            
            # Check for slow query
            if execution_time_ms > self.SLOW_QUERY_THRESHOLD_MS:
                self._stats["slow_queries"] += 1
                self._slow_queries.append({
                    "timestamp": datetime.now().isoformat(),
                    "query_id": query_id,
                    "execution_time_ms": execution_time_ms,
                    "sql_hash": sql_hash
                })
                
                if execution_time_ms > self.VERY_SLOW_QUERY_THRESHOLD_MS:
                    self._trigger_alert(
                        "very_slow_query",
                        f"Query took {execution_time_ms}ms: {sql_hash}"
                    )
            
            # Update per-query health
            self._update_query_health(sql_hash, execution)
    
    def _update_query_health(self, sql_hash: str, execution: QueryExecution) -> None:
        """Update health tracking for a specific query."""
        if sql_hash not in self._query_health:
            self._query_health[sql_hash] = QueryHealth(sql_hash=sql_hash)
        
        health = self._query_health[sql_hash]
        health.total_executions += 1
        health.total_time_ms += execution.execution_time_ms
        health.min_time_ms = min(health.min_time_ms, execution.execution_time_ms)
        health.max_time_ms = max(health.max_time_ms, execution.execution_time_ms)
        health.last_execution = execution.timestamp
        
        if execution.status == QueryStatus.SUCCESS:
            health.successful_executions += 1
            health.consecutive_failures = 0
        else:
            health.failed_executions += 1
            health.consecutive_failures += 1
        
        # Update circuit status
        health.is_circuit_open = self._circuit_breaker.is_open(sql_hash)
        if health.is_circuit_open:
            health.circuit_opened_at = self._circuit_breaker._opened_at.get(sql_hash)
    
    def _trigger_alert(self, alert_type: str, message: str) -> None:
        """Trigger an alert via registered callbacks."""
        for callback in self._alert_callbacks:
            try:
                callback(alert_type, message)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def is_query_allowed(self, sql: str) -> tuple:
        """
        Check if a query is allowed to execute.
        Returns (allowed, reason).
        """
        import hashlib
        sql_hash = hashlib.md5(sql.encode()).hexdigest()[:16]
        
        if self._circuit_breaker.is_open(sql_hash):
            return False, f"Circuit breaker is open for this query (hash: {sql_hash})"
        
        return True, ""
    
    def get_query_health(self, sql: str) -> Optional[QueryHealth]:
        """Get health status for a specific query."""
        import hashlib
        sql_hash = hashlib.md5(sql.encode()).hexdigest()[:16]
        return self._query_health.get(sql_hash)
    
    def get_all_query_health(self) -> Dict[str, QueryHealth]:
        """Get health status for all tracked queries."""
        return self._query_health.copy()
    
    def get_slow_queries(self, limit: int = 20) -> List[Dict]:
        """Get recent slow queries."""
        return list(self._slow_queries)[-limit:]
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent query errors."""
        return list(self._recent_errors)[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        with self._lock:
            stats = self._stats.copy()
            
            # Calculate averages
            if stats["total_queries"] > 0:
                stats["avg_time_ms"] = round(
                    stats["total_time_ms"] / stats["total_queries"], 2
                )
                stats["success_rate"] = round(
                    stats["total_successes"] / stats["total_queries"], 3
                )
            else:
                stats["avg_time_ms"] = 0
                stats["success_rate"] = 0
            
            stats["queries_with_open_circuits"] = sum(
                1 for h in self._query_health.values() if h.is_circuit_open
            )
            stats["unique_queries_tracked"] = len(self._query_health)
            
            return stats
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        stats = self.get_stats()
        
        # Get top slow queries
        slow_queries = sorted(
            [h for h in self._query_health.values()],
            key=lambda h: h.avg_time_ms,
            reverse=True
        )[:10]
        
        # Get problematic queries (high failure rate)
        problematic = [
            h for h in self._query_health.values()
            if h.failure_rate > self.HIGH_FAILURE_RATE_THRESHOLD and h.total_executions >= 5
        ]
        
        # Get execution trend (last 24 hours by hour)
        now = datetime.now()
        hourly_stats = {}
        for i in range(24):
            hour = now - timedelta(hours=i)
            hour_key = hour.strftime("%Y-%m-%d %H:00")
            hourly_stats[hour_key] = {"success": 0, "failure": 0}
        
        for execution in self._history:
            hour_key = execution.timestamp.strftime("%Y-%m-%d %H:00")
            if hour_key in hourly_stats:
                if execution.status == QueryStatus.SUCCESS:
                    hourly_stats[hour_key]["success"] += 1
                else:
                    hourly_stats[hour_key]["failure"] += 1
        
        return {
            "stats": stats,
            "slow_queries": [q.to_dict() for q in slow_queries],
            "problematic_queries": [q.to_dict() for q in problematic],
            "recent_errors": self.get_recent_errors(10),
            "hourly_trend": hourly_stats,
            "last_updated": datetime.now().isoformat()
        }
    
    def register_alert_callback(self, callback: Callable) -> None:
        """Register a callback for alerts."""
        self._alert_callbacks.append(callback)
    
    def reset_circuit(self, sql_hash: str) -> None:
        """Manually reset a circuit breaker."""
        self._circuit_breaker.reset(sql_hash)
        if sql_hash in self._query_health:
            self._query_health[sql_hash].is_circuit_open = False
            self._query_health[sql_hash].consecutive_failures = 0
    
    def clear_history(self) -> None:
        """Clear execution history."""
        with self._lock:
            self._history.clear()
            self._slow_queries.clear()
            self._recent_errors.clear()


class QueryTimer:
    """Context manager for timing query execution."""
    
    def __init__(
        self,
        monitor: QueryMonitor,
        query_id: str,
        sql: str,
        source: str = "template"
    ):
        self.monitor = monitor
        self.query_id = query_id
        self.sql = sql
        self.source = source
        self.start_time = None
        self.execution_time_ms = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.execution_time_ms = (time.time() - self.start_time) * 1000
        
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        self.monitor.record_execution(
            query_id=self.query_id,
            sql=self.sql,
            execution_time_ms=self.execution_time_ms,
            success=success,
            error_message=error_message,
            source=self.source
        )
        
        # Don't suppress exceptions
        return False


# Global singleton
_query_monitor: Optional[QueryMonitor] = None
_monitor_lock = threading.Lock()


def get_query_monitor() -> QueryMonitor:
    """Get the global query monitor instance."""
    global _query_monitor
    
    with _monitor_lock:
        if _query_monitor is None:
            _query_monitor = QueryMonitor()
        return _query_monitor


def time_query(query_id: str, sql: str, source: str = "template") -> QueryTimer:
    """Create a query timer context manager."""
    return QueryTimer(get_query_monitor(), query_id, sql, source)
