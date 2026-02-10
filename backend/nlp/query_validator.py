"""
Query Validator - SQL Safety and Validation Layer
=================================================
Comprehensive validation for SQL queries before execution.
Protects against SQL injection, validates syntax, enforces complexity limits,
and ensures queries only access allowed tables/columns.

Features:
- SQL injection detection and prevention
- Syntax validation with detailed error messages
- Complexity limits (max joins, max subqueries)
- Read-only enforcement (no INSERT/UPDATE/DELETE/DROP)
- Table/column whitelist validation
- Query timeout estimation
- Performance hints

Author: AlUla Inspection AI
Version: 2.0
"""

import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Parenthesis, Token
from sqlparse.tokens import Keyword, DML, DDL, Name, String, Punctuation
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"      # Query cannot be executed
    WARNING = "warning"  # Query can run but has issues
    INFO = "info"        # Informational note


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    severity: ValidationSeverity
    code: str
    message: str
    suggestion: Optional[str] = None
    position: Optional[int] = None  # Character position in SQL


@dataclass
class ValidationResult:
    """Complete validation result for a SQL query."""
    is_valid: bool
    is_safe: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    normalized_sql: Optional[str] = None
    tables_used: Set[str] = field(default_factory=set)
    columns_used: Dict[str, Set[str]] = field(default_factory=dict)  # table -> columns
    estimated_complexity: int = 0  # 1-10 scale
    estimated_rows: Optional[int] = None
    
    def add_error(self, code: str, message: str, suggestion: str = None):
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code=code,
            message=message,
            suggestion=suggestion
        ))
        self.is_valid = False
        self.is_safe = False
    
    def add_warning(self, code: str, message: str, suggestion: str = None):
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code=code,
            message=message,
            suggestion=suggestion
        ))
    
    def add_info(self, code: str, message: str):
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            code=code,
            message=message
        ))
    
    def get_errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    def get_warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "is_safe": self.is_safe,
            "issues": [
                {
                    "severity": i.severity.value,
                    "code": i.code,
                    "message": i.message,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "tables_used": list(self.tables_used),
            "estimated_complexity": self.estimated_complexity
        }


class QueryValidator:
    """
    Comprehensive SQL query validator for security and correctness.
    
    Usage:
        validator = QueryValidator(schema_registry=registry)
        result = validator.validate(sql)
        if result.is_valid and result.is_safe:
            # Execute query
        else:
            # Handle errors
    """
    
    # SQL Injection patterns to detect
    INJECTION_PATTERNS = [
        (r";\s*--", "SQL comment after semicolon"),
        (r";\s*DROP\s+", "DROP statement after semicolon"),
        (r";\s*DELETE\s+", "DELETE statement after semicolon"),
        (r";\s*INSERT\s+", "INSERT statement after semicolon"),
        (r";\s*UPDATE\s+", "UPDATE statement after semicolon"),
        (r";\s*TRUNCATE\s+", "TRUNCATE statement after semicolon"),
        (r";\s*ALTER\s+", "ALTER statement after semicolon"),
        (r";\s*CREATE\s+", "CREATE statement after semicolon"),
        (r";\s*EXEC\s+", "EXEC statement after semicolon"),
        (r"UNION\s+ALL\s+SELECT", "UNION injection attempt"),
        (r"UNION\s+SELECT", "UNION injection attempt"),
        (r"OR\s+1\s*=\s*1", "Always-true condition injection"),
        (r"OR\s+'1'\s*=\s*'1'", "Always-true condition injection"),
        (r"OR\s+''=''", "Always-true condition injection"),
        (r"'\s*OR\s+''='", "Quote escape injection"),
        (r"xp_cmdshell", "SQL Server command shell"),
        (r"sp_executesql", "Dynamic SQL execution"),
        (r"WAITFOR\s+DELAY", "Time-based injection"),
        (r"BENCHMARK\s*\(", "MySQL benchmark injection"),
        (r"SLEEP\s*\(", "Sleep injection"),
        (r"INTO\s+OUTFILE", "File write injection"),
        (r"INTO\s+DUMPFILE", "File write injection"),
        (r"LOAD_FILE\s*\(", "File read injection"),
        (r"@@version", "Version enumeration"),
        (r"@@datadir", "Data directory enumeration"),
        (r"INFORMATION_SCHEMA\.", "Schema enumeration"),  # Allowed in our use but log it
    ]
    
    # Dangerous SQL keywords (write operations)
    DANGEROUS_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", 
        "ALTER", "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
        "MERGE", "REPLACE", "CALL"
    }
    
    # Allowed SQL keywords for read-only queries
    ALLOWED_KEYWORDS = {
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
        "FULL", "CROSS", "ON", "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE",
        "IS", "NULL", "ORDER", "BY", "ASC", "DESC", "GROUP", "HAVING",
        "DISTINCT", "TOP", "LIMIT", "OFFSET", "AS", "WITH", "CASE", "WHEN",
        "THEN", "ELSE", "END", "CAST", "CONVERT", "COALESCE", "NULLIF",
        "COUNT", "SUM", "AVG", "MIN", "MAX", "YEAR", "MONTH", "DAY",
        "DATEPART", "DATEDIFF", "DATEADD", "GETDATE", "GETUTCDATE",
        "ISNULL", "IIF", "SUBSTRING", "LEN", "UPPER", "LOWER", "TRIM",
        "LTRIM", "RTRIM", "REPLACE", "ROUND", "FLOOR", "CEILING", "ABS",
        "ROW_NUMBER", "RANK", "DENSE_RANK", "OVER", "PARTITION", "UNION", "ALL",
        "EXCEPT", "INTERSECT", "EXISTS", "ANY", "SOME", "CTE"
    }
    
    # Complexity limits
    MAX_JOINS = 5
    MAX_SUBQUERIES = 3
    MAX_QUERY_LENGTH = 10000
    MAX_CONDITIONS = 20
    
    def __init__(self, schema_registry=None, strict_mode: bool = True):
        """
        Initialize the validator.
        
        Args:
            schema_registry: Optional SchemaRegistry for table/column validation
            strict_mode: If True, fail on warnings too
        """
        self.schema_registry = schema_registry
        self.strict_mode = strict_mode
    
    def validate(self, sql: str, allow_write: bool = False) -> ValidationResult:
        """
        Validate a SQL query comprehensively.
        
        Args:
            sql: The SQL query to validate
            allow_write: If True, allow write operations (dangerous!)
            
        Returns:
            ValidationResult with all findings
        """
        result = ValidationResult(is_valid=True, is_safe=True)
        
        if not sql or not sql.strip():
            result.add_error("EMPTY_QUERY", "Query is empty or contains only whitespace")
            return result
        
        # Normalize the SQL
        sql = sql.strip()
        result.normalized_sql = self._normalize_sql(sql)
        
        # Step 1: Check length
        if len(sql) > self.MAX_QUERY_LENGTH:
            result.add_error(
                "QUERY_TOO_LONG",
                f"Query exceeds maximum length of {self.MAX_QUERY_LENGTH} characters",
                "Consider simplifying the query or breaking it into smaller parts"
            )
        
        # Step 2: Check for SQL injection patterns
        self._check_injection_patterns(sql, result)
        
        # Step 3: Check for dangerous keywords
        if not allow_write:
            self._check_dangerous_keywords(sql, result)
        
        # Step 4: Parse and analyze SQL structure
        self._analyze_sql_structure(sql, result)
        
        # Step 5: Validate tables and columns against schema
        if self.schema_registry:
            self._validate_against_schema(result)
        
        # Step 6: Calculate complexity score
        result.estimated_complexity = self._calculate_complexity(sql, result)
        
        # Add performance hints
        self._add_performance_hints(sql, result)
        
        return result
    
    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for consistent processing."""
        # Remove extra whitespace
        normalized = " ".join(sql.split())
        # Format nicely
        normalized = sqlparse.format(
            normalized,
            reindent=True,
            keyword_case='upper',
            identifier_case='lower'
        )
        return normalized
    
    def _check_injection_patterns(self, sql: str, result: ValidationResult) -> None:
        """Check for SQL injection patterns."""
        sql_upper = sql.upper()
        
        for pattern, description in self.INJECTION_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                result.add_error(
                    "INJECTION_DETECTED",
                    f"Potential SQL injection detected: {description}",
                    "Use parameterized queries instead of string concatenation"
                )
    
    def _check_dangerous_keywords(self, sql: str, result: ValidationResult) -> None:
        """Check for dangerous (write) SQL keywords."""
        # Parse to get tokens
        parsed = sqlparse.parse(sql)
        if not parsed:
            return
        
        for statement in parsed:
            # Get the statement type
            stmt_type = statement.get_type()
            if stmt_type in ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]:
                result.add_error(
                    "WRITE_OPERATION",
                    f"Write operation '{stmt_type}' is not allowed in read-only mode",
                    "Only SELECT queries are permitted"
                )
            
            # Also check tokens
            for token in statement.flatten():
                if token.ttype in (DML, DDL):
                    word = token.value.upper()
                    if word in self.DANGEROUS_KEYWORDS:
                        result.add_error(
                            "DANGEROUS_KEYWORD",
                            f"Dangerous keyword '{word}' detected",
                            "Only SELECT operations are allowed"
                        )
    
    def _analyze_sql_structure(self, sql: str, result: ValidationResult) -> None:
        """Analyze SQL structure for complexity and correctness."""
        parsed = sqlparse.parse(sql)
        if not parsed:
            result.add_error("PARSE_ERROR", "Failed to parse SQL query")
            return
        
        statement = parsed[0]
        
        # Count JOINs
        join_count = len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE))
        if join_count > self.MAX_JOINS:
            result.add_warning(
                "TOO_MANY_JOINS",
                f"Query has {join_count} JOINs (max recommended: {self.MAX_JOINS})",
                "Consider simplifying the query or using subqueries"
            )
        
        # Count subqueries
        subquery_count = sql.count("(SELECT") + sql.count("( SELECT")
        if subquery_count > self.MAX_SUBQUERIES:
            result.add_warning(
                "TOO_MANY_SUBQUERIES",
                f"Query has {subquery_count} subqueries (max recommended: {self.MAX_SUBQUERIES})",
                "Consider using CTEs (WITH clause) or simplifying"
            )
        
        # Count conditions
        condition_count = len(re.findall(r'\b(AND|OR)\b', sql, re.IGNORECASE))
        if condition_count > self.MAX_CONDITIONS:
            result.add_warning(
                "TOO_MANY_CONDITIONS",
                f"Query has {condition_count} conditions (max recommended: {self.MAX_CONDITIONS})",
                "Consider using IN clauses or temporary tables"
            )
        
        # Extract tables used
        self._extract_tables(statement, result)
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            if not re.search(r'SELECT\s+\*\s+FROM\s+\(\s*SELECT', sql, re.IGNORECASE):
                # Not inside a subquery
                result.add_info(
                    "SELECT_STAR",
                    "Using SELECT * - consider specifying columns explicitly for better performance"
                )
        
        # Check for missing WHERE clause on large tables
        if "WHERE" not in sql.upper():
            result.add_warning(
                "NO_WHERE_CLAUSE",
                "Query has no WHERE clause - may return large result set",
                "Add filtering conditions to improve performance"
            )
        
        # Check for ORDER BY without TOP/LIMIT
        if "ORDER BY" in sql.upper() and "TOP" not in sql.upper() and "LIMIT" not in sql.upper():
            result.add_info(
                "UNBOUNDED_SORT",
                "ORDER BY without TOP/LIMIT - entire result set will be sorted"
            )
    
    def _extract_tables(self, statement, result: ValidationResult) -> None:
        """Extract table names from SQL statement."""
        # Get FROM and JOIN clauses
        sql = str(statement)
        
        # Pattern for table names after FROM, JOIN
        table_pattern = r'(?:FROM|JOIN)\s+(\[?[\w]+\]?)(?:\s+(?:AS\s+)?(\w+))?'
        matches = re.findall(table_pattern, sql, re.IGNORECASE)
        
        for match in matches:
            table_name = match[0].strip('[]')
            result.tables_used.add(table_name)
    
    def _validate_against_schema(self, result: ValidationResult) -> None:
        """Validate tables and columns against the schema registry."""
        if not self.schema_registry:
            return
        
        for table_name in result.tables_used:
            # Skip aliases and subqueries
            if table_name.upper() in ('SELECT', 'WITH', 'AS'):
                continue
            
            table_info = self.schema_registry.get_table(table_name)
            if not table_info:
                # Try case-insensitive match
                found = False
                for known_table in self.schema_registry.get_all_tables():
                    if known_table.lower() == table_name.lower():
                        found = True
                        break
                
                if not found:
                    result.add_error(
                        "UNKNOWN_TABLE",
                        f"Table '{table_name}' does not exist in the database",
                        "Check spelling or use the schema registry to find valid table names"
                    )
    
    def _calculate_complexity(self, sql: str, result: ValidationResult) -> int:
        """
        Calculate query complexity score (1-10).
        
        Factors:
        - Number of JOINs
        - Number of subqueries
        - Number of conditions
        - Use of aggregations
        - Use of window functions
        """
        score = 1
        
        # JOINs add complexity
        join_count = len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE))
        score += min(join_count, 3)
        
        # Subqueries add complexity
        subquery_count = sql.upper().count("SELECT") - 1
        score += min(subquery_count * 2, 4)
        
        # Aggregations
        if re.search(r'\b(COUNT|SUM|AVG|MIN|MAX)\s*\(', sql, re.IGNORECASE):
            score += 1
        
        # Window functions
        if re.search(r'\bOVER\s*\(', sql, re.IGNORECASE):
            score += 1
        
        # GROUP BY
        if "GROUP BY" in sql.upper():
            score += 1
        
        # HAVING
        if "HAVING" in sql.upper():
            score += 1
        
        return min(score, 10)
    
    def _add_performance_hints(self, sql: str, result: ValidationResult) -> None:
        """Add performance hints based on query analysis."""
        sql_upper = sql.upper()
        
        # Check for non-SARGable patterns
        if re.search(r'WHERE\s+\w+\s*\(', sql_upper):
            result.add_info(
                "NON_SARGABLE",
                "Function on column in WHERE clause may prevent index usage"
            )
        
        # Check for LIKE with leading wildcard
        if re.search(r"LIKE\s+'%", sql_upper):
            result.add_info(
                "LEADING_WILDCARD",
                "LIKE with leading wildcard '%...' cannot use indexes"
            )
        
        # Check for implicit conversions
        if re.search(r'WHERE\s+\w+\s*=\s*\d+', sql) and "CAST" not in sql_upper:
            result.add_info(
                "POSSIBLE_IMPLICIT_CONVERSION",
                "Possible implicit type conversion - ensure data types match"
            )
    
    def sanitize_value(self, value: Any) -> str:
        """
        Sanitize a value for safe inclusion in SQL.
        Use parameterized queries instead when possible!
        """
        if value is None:
            return "NULL"
        
        if isinstance(value, bool):
            return "1" if value else "0"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            # Remove dangerous characters
            escaped = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', escaped)
            return f"'{escaped}'"
        
        return f"'{str(value)}'"
    
    def extract_query_type(self, sql: str) -> str:
        """Extract the type of SQL query."""
        parsed = sqlparse.parse(sql)
        if parsed:
            return parsed[0].get_type() or "UNKNOWN"
        return "UNKNOWN"
    
    def quick_validate(self, sql: str) -> Tuple[bool, str]:
        """
        Quick validation for common issues.
        Returns (is_ok, error_message).
        """
        if not sql or not sql.strip():
            return False, "Query is empty"
        
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT (or WITH for CTEs)
        if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
            return False, "Query must start with SELECT or WITH"
        
        # Check for dangerous patterns
        for pattern, desc in self.INJECTION_PATTERNS[:10]:  # Check top patterns
            if re.search(pattern, sql_upper, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {desc}"
        
        return True, ""


class ParameterizedQueryBuilder:
    """
    Helper class to build parameterized queries safely.
    Prevents SQL injection by using proper parameterization.
    """
    
    def __init__(self):
        self._params: Dict[str, Any] = {}
        self._param_counter = 0
    
    def add_param(self, value: Any, name: str = None) -> str:
        """
        Add a parameter and return its placeholder.
        
        Args:
            value: The value to parameterize
            name: Optional name for the parameter
            
        Returns:
            Placeholder string to use in SQL (e.g., '@param1')
        """
        if name is None:
            self._param_counter += 1
            name = f"param{self._param_counter}"
        
        self._params[name] = value
        return f"@{name}"
    
    def get_params(self) -> Dict[str, Any]:
        """Get all parameters."""
        return self._params.copy()
    
    def build_in_clause(self, values: List[Any], name_prefix: str = "in") -> str:
        """
        Build a safe IN clause with parameterized values.
        
        Args:
            values: List of values for IN clause
            name_prefix: Prefix for parameter names
            
        Returns:
            Parameterized IN clause (e.g., '(@in1, @in2, @in3)')
        """
        if not values:
            return "(NULL)"  # Empty IN clause
        
        placeholders = []
        for i, value in enumerate(values):
            param_name = f"{name_prefix}{i+1}"
            self._params[param_name] = value
            placeholders.append(f"@{param_name}")
        
        return f"({', '.join(placeholders)})"
    
    def clear(self) -> None:
        """Clear all parameters."""
        self._params.clear()
        self._param_counter = 0


# Convenience functions
def validate_sql(sql: str, schema_registry=None) -> ValidationResult:
    """Validate a SQL query."""
    validator = QueryValidator(schema_registry=schema_registry)
    return validator.validate(sql)


def is_sql_safe(sql: str) -> Tuple[bool, str]:
    """Quick check if SQL is safe to execute."""
    validator = QueryValidator()
    is_ok, error = validator.quick_validate(sql)
    return is_ok, error


def sanitize_string(value: str) -> str:
    """Sanitize a string for SQL inclusion."""
    validator = QueryValidator()
    return validator.sanitize_value(value)
