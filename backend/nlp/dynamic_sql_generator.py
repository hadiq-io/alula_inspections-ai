"""
Dynamic SQL Generator - AI-Powered Query Generation
====================================================
The heart of the intelligent query system. Uses Claude AI to generate
SQL queries dynamically based on natural language questions and database schema.

Features:
- Chain-of-thought SQL generation with Claude
- Schema-aware query building
- Automatic JOIN inference
- Query validation before execution
- Self-correction on validation errors
- Bilingual support (English/Arabic)
- Query explanation generation

Author: AlUla Inspection AI
Version: 2.0
"""

import os
import re
import json
import httpx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import hashlib

from .schema_registry import SchemaRegistry, get_schema_registry, SemanticAnnotations
from .query_validator import QueryValidator, ValidationResult


@dataclass
class GeneratedQuery:
    """Represents a dynamically generated SQL query."""
    sql: str
    explanation: str
    explanation_ar: str
    tables_used: List[str]
    confidence: float  # 0.0 to 1.0
    generation_time_ms: int
    chart_suggestion: Optional[str] = None
    query_type: str = "SELECT"  # SELECT, AGGREGATE, RANKING, etc.
    is_valid: bool = True
    validation_result: Optional[ValidationResult] = None
    
    # For learning system
    question_pattern: Optional[str] = None
    intent: Optional[str] = None
    entities_used: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sql": self.sql,
            "explanation": self.explanation,
            "explanation_ar": self.explanation_ar,
            "tables_used": self.tables_used,
            "confidence": self.confidence,
            "generation_time_ms": self.generation_time_ms,
            "chart_suggestion": self.chart_suggestion,
            "query_type": self.query_type,
            "is_valid": self.is_valid,
            "question_pattern": self.question_pattern,
            "intent": self.intent
        }


class DynamicSQLGenerator:
    """
    AI-powered SQL query generator using Claude.
    
    This is the magic component that allows the system to handle
    ANY question, not just predefined templates.
    
    Strategy:
    1. Analyze the question to understand intent
    2. Identify relevant tables/columns from schema
    3. Use Claude to generate SQL with chain-of-thought
    4. Validate the generated SQL
    5. Self-correct if validation fails
    6. Return query with explanation
    """
    
    # SQL Server specific date functions
    DATE_FUNCTIONS = {
        "year": "YEAR({column})",
        "month": "MONTH({column})",
        "day": "DAY({column})",
        "quarter": "DATEPART(QUARTER, {column})",
        "week": "DATEPART(WEEK, {column})",
        "dayofweek": "DATEPART(WEEKDAY, {column})"
    }
    
    # Common aggregation mappings
    AGGREGATIONS = {
        "count": "COUNT",
        "total": "COUNT",
        "sum": "SUM",
        "average": "AVG",
        "mean": "AVG",
        "maximum": "MAX",
        "minimum": "MIN",
        "highest": "MAX",
        "lowest": "MIN"
    }
    
    def __init__(
        self,
        schema_registry: SchemaRegistry = None,
        azure_endpoint: str = None,
        azure_api_key: str = None,
        max_retries: int = 2
    ):
        """
        Initialize the dynamic SQL generator.
        
        Args:
            schema_registry: Schema registry for table/column info
            azure_endpoint: Azure OpenAI endpoint
            azure_api_key: Azure API key
            max_retries: Max retries for self-correction
        """
        self.schema_registry = schema_registry or get_schema_registry()
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = azure_api_key or os.getenv("AZURE_OPENAI_KEY")
        self.model_name = os.getenv("AZURE_MODEL_NAME", "claude-sonnet-4-5")
        self.validator = QueryValidator(schema_registry=self.schema_registry)
        self.max_retries = max_retries
        
        # Generation statistics
        self._stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "validation_failures": 0,
            "self_corrections": 0
        }
    
    def generate(
        self,
        question: str,
        parsed_query: Dict[str, Any] = None,
        language: str = "en",
        context: str = None
    ) -> GeneratedQuery:
        """
        Generate a SQL query for a natural language question.
        
        Args:
            question: Natural language question
            parsed_query: Pre-parsed query info (intent, entities, etc.)
            language: Response language
            context: Additional context from conversation
            
        Returns:
            GeneratedQuery with SQL and metadata
        """
        start_time = datetime.now()
        self._stats["total_generations"] += 1
        
        try:
            # Step 1: Get relevant schema context
            schema_context = self._get_schema_context(question, parsed_query)
            
            # Step 2: Build the prompt
            prompt = self._build_generation_prompt(
                question=question,
                parsed_query=parsed_query,
                schema_context=schema_context,
                context=context
            )
            
            # Step 3: Call Claude to generate SQL
            response = self._call_claude(prompt)
            
            # Step 4: Parse the response
            sql, explanation, metadata = self._parse_claude_response(response)
            
            # Step 5: Validate the SQL
            validation = self.validator.validate(sql)
            
            # Step 6: Self-correct if validation failed
            if not validation.is_valid and self.max_retries > 0:
                sql, explanation, validation = self._self_correct(
                    question=question,
                    original_sql=sql,
                    validation_result=validation,
                    schema_context=schema_context,
                    retries_left=self.max_retries
                )
            
            # Calculate timing
            generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Build result
            result = GeneratedQuery(
                sql=sql,
                explanation=explanation,
                explanation_ar=self._translate_explanation(explanation) if language == "ar" else "",
                tables_used=list(validation.tables_used),
                confidence=self._calculate_confidence(validation, metadata),
                generation_time_ms=generation_time,
                chart_suggestion=metadata.get("chart_type"),
                query_type=metadata.get("query_type", "SELECT"),
                is_valid=validation.is_valid,
                validation_result=validation,
                question_pattern=self._extract_pattern(question),
                intent=parsed_query.get("intent") if parsed_query else None,
                entities_used=parsed_query.get("entities", {}) if parsed_query else {}
            )
            
            if validation.is_valid:
                self._stats["successful_generations"] += 1
            else:
                self._stats["validation_failures"] += 1
            
            return result
            
        except Exception as e:
            # Return error result
            generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return GeneratedQuery(
                sql="",
                explanation=f"Failed to generate query: {str(e)}",
                explanation_ar=f"فشل في إنشاء الاستعلام: {str(e)}",
                tables_used=[],
                confidence=0.0,
                generation_time_ms=generation_time,
                is_valid=False
            )
    
    def _get_schema_context(self, question: str, parsed_query: Dict = None) -> str:
        """Get relevant schema context for the question."""
        # Find relevant concepts
        concepts = SemanticAnnotations.get_concept_for_keywords(question)
        
        # Add concepts from parsed query
        if parsed_query:
            metric = parsed_query.get("metric", "")
            if metric:
                concepts.extend(SemanticAnnotations.get_concept_for_keywords(metric))
        
        # Get schema context
        return self.schema_registry.get_schema_context_for_ai(
            concepts=concepts if concepts else None,
            include_all_core=True
        )
    
    def _build_generation_prompt(
        self,
        question: str,
        parsed_query: Dict,
        schema_context: str,
        context: str = None
    ) -> str:
        """Build the prompt for Claude to generate SQL."""
        
        # Extract key info from parsed query
        intent = parsed_query.get("intent", "COUNT") if parsed_query else "COUNT"
        entities = parsed_query.get("entities", {}) if parsed_query else {}
        time_period = parsed_query.get("time_period", {}) if parsed_query else {}
        
        prompt = f"""You are an expert SQL developer for Microsoft SQL Server. Generate a SQL query for the following question about an inspection/compliance database in AlUla, Saudi Arabia.

## DATABASE SCHEMA
{schema_context}

## USER QUESTION
"{question}"

## PARSED INFORMATION
- Intent: {intent}
- Entities: {json.dumps(entities, ensure_ascii=False)}
- Time Period: {json.dumps(time_period, ensure_ascii=False)}

## INSTRUCTIONS
1. Generate a valid SQL Server query (T-SQL syntax)
2. Use appropriate JOINs based on the schema relationships
3. Always filter with IsDeleted = 0 for Event and Locations tables
4. Use TOP 100 for result limiting unless aggregating
5. Include both English and Arabic columns when available (Name, NameAr)
6. Format dates using YEAR(), MONTH() for grouping
7. Use meaningful column aliases

## CHAIN OF THOUGHT
Before writing SQL, think through:
1. Which tables are needed?
2. What JOINs are required?
3. What columns to SELECT?
4. What WHERE conditions?
5. Any GROUP BY or ORDER BY needed?

## RESPONSE FORMAT
Respond with a JSON object:
{{
    "thinking": "Your chain of thought reasoning",
    "tables_needed": ["table1", "table2"],
    "sql": "YOUR SQL QUERY HERE",
    "explanation": "Brief explanation of what the query does",
    "query_type": "SELECT|AGGREGATE|RANKING|TREND|COMPARISON",
    "chart_type": "bar|line|pie|none"
}}

IMPORTANT:
- Only generate SELECT queries (read-only)
- Handle NULL values with COALESCE/ISNULL
- Use proper date filtering for time periods
- Be aware this is Arabic/English bilingual data"""

        if context:
            prompt += f"\n\n## CONVERSATION CONTEXT\n{context}"
        
        return prompt
    
    def _call_claude(self, prompt: str) -> str:
        """Call Claude API to generate SQL."""
        if not self.azure_endpoint or not self.azure_api_key:
            raise ValueError("Azure credentials not configured")
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.azure_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_name,
            "max_tokens": 2000,
            "temperature": 0.1,  # Low temperature for more deterministic SQL
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Handle different endpoint formats
        endpoint = self.azure_endpoint
        if not endpoint.endswith('/messages'):
            endpoint = endpoint.rstrip('/') + '/messages'
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                endpoint,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content from Claude response
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0].get("text", "")
            
            raise ValueError("Empty response from Claude")
    
    def _parse_claude_response(self, response: str) -> Tuple[str, str, Dict]:
        """Parse Claude's response to extract SQL and metadata."""
        # Try to parse as JSON first
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                sql = data.get("sql", "").strip()
                explanation = data.get("explanation", "Query generated by AI")
                metadata = {
                    "query_type": data.get("query_type", "SELECT"),
                    "chart_type": data.get("chart_type", "bar"),
                    "tables_needed": data.get("tables_needed", []),
                    "thinking": data.get("thinking", "")
                }
                return sql, explanation, metadata
        except json.JSONDecodeError:
            pass
        
        # Fallback: extract SQL from code blocks
        sql_match = re.search(r'```sql\s*([\s\S]*?)\s*```', response, re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1).strip()
        else:
            # Try to find SELECT statement
            sql_match = re.search(r'(SELECT[\s\S]*?)(?:;|\n\n|$)', response, re.IGNORECASE)
            sql = sql_match.group(1).strip() if sql_match else ""
        
        return sql, "Query generated by AI", {"query_type": "SELECT", "chart_type": "bar"}
    
    def _self_correct(
        self,
        question: str,
        original_sql: str,
        validation_result: ValidationResult,
        schema_context: str,
        retries_left: int
    ) -> Tuple[str, str, ValidationResult]:
        """Attempt to self-correct a failed query."""
        self._stats["self_corrections"] += 1
        
        if retries_left <= 0:
            return original_sql, "Query could not be validated", validation_result
        
        # Build correction prompt
        errors = "\n".join([f"- {i.message}" for i in validation_result.get_errors()])
        
        correction_prompt = f"""The SQL query I generated has validation errors. Please fix them.

## ORIGINAL QUESTION
"{question}"

## ORIGINAL SQL (WITH ERRORS)
```sql
{original_sql}
```

## VALIDATION ERRORS
{errors}

## DATABASE SCHEMA
{schema_context}

## INSTRUCTIONS
1. Fix ALL the validation errors
2. Maintain the original query intent
3. Use only tables and columns from the schema
4. Return ONLY the corrected SQL query

## RESPONSE FORMAT
Respond with just the corrected SQL query, no explanation needed.
```sql
YOUR CORRECTED SQL HERE
```"""

        try:
            response = self._call_claude(correction_prompt)
            
            # Extract SQL
            sql_match = re.search(r'```sql\s*([\s\S]*?)\s*```', response, re.IGNORECASE)
            if sql_match:
                corrected_sql = sql_match.group(1).strip()
            else:
                corrected_sql = response.strip()
            
            # Validate again
            new_validation = self.validator.validate(corrected_sql)
            
            if new_validation.is_valid:
                return corrected_sql, "Query generated and corrected by AI", new_validation
            
            # Recurse if still invalid
            return self._self_correct(
                question, corrected_sql, new_validation, 
                schema_context, retries_left - 1
            )
            
        except Exception as e:
            return original_sql, f"Self-correction failed: {e}", validation_result
    
    def _calculate_confidence(self, validation: ValidationResult, metadata: Dict) -> float:
        """Calculate confidence score for the generated query."""
        confidence = 1.0
        
        # Reduce for validation issues
        confidence -= len(validation.get_errors()) * 0.3
        confidence -= len(validation.get_warnings()) * 0.1
        
        # Reduce for high complexity
        if validation.estimated_complexity > 7:
            confidence -= 0.1
        
        # Boost if we have clear thinking
        if metadata.get("thinking"):
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_pattern(self, question: str) -> str:
        """Extract a reusable pattern from the question."""
        # Remove specific values to create a pattern
        pattern = question.lower()
        
        # Replace years
        pattern = re.sub(r'\b20\d{2}\b', '{year}', pattern)
        
        # Replace months
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        for month in months:
            pattern = re.sub(rf'\b{month}\b', '{month}', pattern, flags=re.IGNORECASE)
        
        # Replace numbers
        pattern = re.sub(r'\b\d+\b', '{number}', pattern)
        
        # Replace quoted strings
        pattern = re.sub(r'"[^"]*"', '{value}', pattern)
        pattern = re.sub(r"'[^']*'", '{value}', pattern)
        
        return pattern.strip()
    
    def _translate_explanation(self, explanation: str) -> str:
        """Translate explanation to Arabic (simplified)."""
        # Basic translation mappings
        translations = {
            "Query": "استعلام",
            "counts": "يحسب",
            "inspections": "التفتيشات",
            "violations": "المخالفات",
            "locations": "المواقع",
            "by": "حسب",
            "year": "السنة",
            "month": "الشهر",
            "total": "إجمالي",
            "average": "متوسط",
            "from": "من",
            "the database": "قاعدة البيانات"
        }
        
        result = explanation
        for en, ar in translations.items():
            result = result.replace(en, ar)
        
        return result
    
    def generate_for_unknown_concept(
        self,
        question: str,
        concept: str,
        language: str = "en"
    ) -> GeneratedQuery:
        """
        Special generation for completely unknown concepts (like Health Certificates).
        This method searches the schema for related columns and builds a discovery query.
        """
        # Search schema for related columns
        related_columns = self.schema_registry.search_columns(concept)
        
        if not related_columns:
            # Try variations
            variations = [
                concept,
                concept.replace(" ", ""),
                concept.replace(" ", "_"),
                concept.split()[0] if " " in concept else concept
            ]
            
            for variation in variations:
                related_columns = self.schema_registry.search_columns(variation)
                if related_columns:
                    break
        
        if related_columns:
            # Found related columns - generate specific query
            tables = list(set([tc[0] for tc in related_columns]))
            columns = [f"{tc[0]}.{tc[1]}" for tc in related_columns[:5]]
            
            # Build a discovery query
            discovery_prompt = f"""Generate a SQL query to explore '{concept}' data.

## RELATED COLUMNS FOUND
{json.dumps([(tc[0], tc[1], tc[2].data_type) for tc in related_columns[:10]], indent=2)}

## TABLES WITH THIS DATA
{', '.join(tables)}

## USER QUESTION
"{question}"

Generate a query that:
1. Shows relevant {concept} information
2. Includes counts or aggregations if appropriate
3. JOINs with core tables (Event, Locations) if possible
4. Limits to TOP 100 results

Return just the SQL query."""

            response = self._call_claude(discovery_prompt)
            sql, explanation, metadata = self._parse_claude_response(response)
            
        else:
            # No related columns found - generate schema exploration query
            sql = """
-- Unable to find specific columns for this concept
-- Showing available tables and columns for exploration
SELECT 
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE
FROM INFORMATION_SCHEMA.TABLES t
JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
WHERE t.TABLE_TYPE = 'BASE TABLE'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
"""
            explanation = f"No specific data found for '{concept}'. Showing database schema for exploration."
        
        # Validate and return
        validation = self.validator.validate(sql)
        
        return GeneratedQuery(
            sql=sql,
            explanation=explanation,
            explanation_ar=self._translate_explanation(explanation),
            tables_used=list(validation.tables_used),
            confidence=0.6 if related_columns else 0.3,
            generation_time_ms=0,
            is_valid=validation.is_valid,
            validation_result=validation,
            question_pattern=self._extract_pattern(question)
        )
    
    def explain_query(self, sql: str, language: str = "en") -> str:
        """Generate a natural language explanation of a SQL query."""
        prompt = f"""Explain this SQL query in simple terms that a non-technical user can understand.

SQL Query:
```sql
{sql}
```

Provide a brief, clear explanation of:
1. What data the query retrieves
2. Any filtering or conditions applied
3. How results are organized

Keep the explanation under 100 words. {"Respond in Arabic." if language == "ar" else ""}"""

        try:
            response = self._call_claude(prompt)
            return response.strip()
        except Exception:
            return "This query retrieves data from the inspection database."
    
    def suggest_improvements(self, sql: str) -> List[Dict[str, str]]:
        """Suggest improvements for a SQL query."""
        validation = self.validator.validate(sql)
        
        suggestions = []
        
        for issue in validation.issues:
            if issue.suggestion:
                suggestions.append({
                    "type": issue.severity.value,
                    "issue": issue.message,
                    "suggestion": issue.suggestion
                })
        
        return suggestions
    
    def stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return self._stats.copy()


# Convenience function for one-off generation
def generate_sql(question: str, parsed_query: Dict = None) -> GeneratedQuery:
    """Generate SQL for a question using default settings."""
    generator = DynamicSQLGenerator()
    return generator.generate(question, parsed_query)
