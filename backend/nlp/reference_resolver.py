"""
Reference Resolver Module
=========================
Resolves contextual references in user questions to make them fully qualified.
Handles references like "last year", "break it down", "top 5", "same period",
"this month", etc. by understanding conversation context.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ReferenceType(Enum):
    """Types of references that can be resolved"""
    TEMPORAL = "temporal"           # Time-related: "last year", "this month"
    COMPARATIVE = "comparative"     # Comparisons: "same as", "compared to"
    QUANTITATIVE = "quantitative"   # Quantities: "top 5", "bottom 10"
    BREAKDOWN = "breakdown"         # Breakdowns: "break it down", "by location"
    ENTITY = "entity"               # Entity refs: "that inspector", "this area"
    AGGREGATION = "aggregation"     # Aggregations: "total", "average"
    FILTER = "filter"               # Filters: "only", "just", "excluding"
    CONTINUATION = "continuation"   # Continue context: "more", "also", "and"


@dataclass
class ResolvedReference:
    """A resolved reference with its SQL components"""
    original_text: str
    reference_type: ReferenceType
    resolved_value: Any
    sql_fragment: Optional[str] = None
    sql_select: Optional[str] = None
    sql_where: Optional[str] = None
    sql_group_by: Optional[str] = None
    sql_order_by: Optional[str] = None
    sql_limit: Optional[str] = None
    confidence: float = 1.0


@dataclass
class ConversationContext:
    """Context from the conversation for reference resolution"""
    current_year: int = field(default_factory=lambda: datetime.now().year)
    current_month: int = field(default_factory=lambda: datetime.now().month)
    last_time_period: Optional[str] = None  # e.g., "2024", "Q1 2024"
    last_entity_type: Optional[str] = None  # e.g., "inspector", "location"
    last_entity_value: Optional[str] = None # e.g., "Ahmed", "Al-Ula Old Town"
    last_aggregation: Optional[str] = None  # e.g., "count", "average"
    last_metric: Optional[str] = None       # e.g., "compliance rate", "violations"
    last_breakdown: Optional[str] = None    # e.g., "by month", "by neighborhood"
    last_limit: Optional[int] = None        # e.g., 10
    mentioned_entities: Dict[str, str] = field(default_factory=dict)
    query_history: List[str] = field(default_factory=list)


class ReferenceResolver:
    """
    Resolves contextual references in user queries.
    
    Features:
    - Temporal resolution: "last year", "previous month", "Q3"
    - Quantitative resolution: "top 5", "bottom 10", "first 3"
    - Breakdown resolution: "break it down", "by location", "per inspector"
    - Entity resolution: "that location", "same inspector", "this area"
    - Comparative resolution: "compared to", "vs", "same period last year"
    - Filter resolution: "only high risk", "just violations", "excluding"
    """
    
    def __init__(self):
        self.context = ConversationContext()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for reference detection"""
        
        # Temporal patterns (English and Arabic)
        self.temporal_patterns = {
            # Year references
            r'\b(last\s+year|previous\s+year)\b': lambda ctx: ctx.current_year - 1,
            r'\b(this\s+year|current\s+year)\b': lambda ctx: ctx.current_year,
            r'\b(next\s+year)\b': lambda ctx: ctx.current_year + 1,
            r'\b(العام الماضي|السنة الماضية)\b': lambda ctx: ctx.current_year - 1,
            r'\b(هذا العام|السنة الحالية)\b': lambda ctx: ctx.current_year,
            
            # Month references
            r'\b(last\s+month|previous\s+month)\b': lambda ctx: self._get_last_month(ctx),
            r'\b(this\s+month|current\s+month)\b': lambda ctx: (ctx.current_year, ctx.current_month),
            r'\b(الشهر الماضي)\b': lambda ctx: self._get_last_month(ctx),
            r'\b(هذا الشهر)\b': lambda ctx: (ctx.current_year, ctx.current_month),
            
            # Week references
            r'\b(last\s+week|previous\s+week)\b': lambda ctx: self._get_last_week(),
            r'\b(this\s+week|current\s+week)\b': lambda ctx: self._get_this_week(),
            
            # Quarter references
            r'\b(last\s+quarter|previous\s+quarter)\b': lambda ctx: self._get_last_quarter(ctx),
            r'\b(this\s+quarter|current\s+quarter)\b': lambda ctx: self._get_current_quarter(ctx),
            r'\bQ([1-4])\b': lambda ctx, m: (ctx.current_year, int(m.group(1))),
            
            # Same period references
            r'\b(same\s+period\s+last\s+year)\b': lambda ctx: self._same_period_last_year(ctx),
            r'\b(year\s+over\s+year|yoy)\b': lambda ctx: "YOY",
            r'\b(month\s+over\s+month|mom)\b': lambda ctx: "MOM",
        }
        
        # Quantitative patterns
        self.quantitative_patterns = {
            r'\b(top|best|highest)\s+(\d+)\b': lambda m: ("DESC", int(m.group(2))),
            r'\b(bottom|worst|lowest)\s+(\d+)\b': lambda m: ("ASC", int(m.group(2))),
            r'\b(first)\s+(\d+)\b': lambda m: ("ASC", int(m.group(2))),
            r'\b(أعلى|أفضل)\s+(\d+)\b': lambda m: ("DESC", int(m.group(2))),
            r'\b(أدنى|أسوأ)\s+(\d+)\b': lambda m: ("ASC", int(m.group(2))),
        }
        
        # Breakdown patterns
        self.breakdown_patterns = {
            r'\b(break\s*(it)?\s*down|breakdown)\b': "breakdown_required",
            r'\b(by\s+location|per\s+location)\b': "Location",
            r'\b(by\s+neighborhood|per\s+neighborhood|by\s+area)\b': "Neighborhood",
            r'\b(by\s+inspector|per\s+inspector)\b': "Inspector",
            r'\b(by\s+month|monthly|per\s+month)\b': "Month",
            r'\b(by\s+week|weekly|per\s+week)\b': "Week",
            r'\b(by\s+day|daily|per\s+day)\b': "Day",
            r'\b(by\s+quarter|quarterly|per\s+quarter)\b': "Quarter",
            r'\b(by\s+violation\s*type|per\s+violation)\b': "ViolationType",
            r'\b(by\s+category)\b': "Category",
            r'\b(حسب الموقع)\b': "Location",
            r'\b(حسب الحي)\b': "Neighborhood",
            r'\b(حسب المفتش)\b': "Inspector",
            r'\b(حسب الشهر)\b': "Month",
        }
        
        # Entity reference patterns
        self.entity_patterns = {
            r'\b(that|the\s+same)\s+(inspector|location|neighborhood|area)\b': "same_entity",
            r'\b(this|that)\s+(one|place|site)\b': "last_entity",
            r'\b(هذا|نفس)\s+(المفتش|الموقع|الحي)\b': "same_entity",
        }
        
        # Comparative patterns
        self.comparative_patterns = {
            r'\b(compared?\s+to|vs\.?|versus)\b': "comparison_required",
            r'\b(more\s+than|greater\s+than|above)\b': "greater",
            r'\b(less\s+than|below|under)\b': "less",
            r'\b(equal\s+to|same\s+as)\b': "equal",
            r'\b(مقارنة بـ|مقابل)\b': "comparison_required",
        }
        
        # Filter patterns
        self.filter_patterns = {
            r'\b(only|just)\s+(high\s*risk|critical)\b': ("RiskLevel", "High"),
            r'\b(only|just)\s+(low\s*risk)\b': ("RiskLevel", "Low"),
            r'\b(only|just)\s+(violations?)\b': ("HasViolations", True),
            r'\b(only|just)\s+(compliant)\b': ("IsCompliant", True),
            r'\b(excluding?|without|except)\s+(\w+)\b': ("exclude", "pattern"),
            r'\b(فقط)\s+(عالية المخاطر)\b': ("RiskLevel", "High"),
        }
        
        # Aggregation patterns
        self.aggregation_patterns = {
            r'\b(total|sum\s+of)\b': "SUM",
            r'\b(average|avg|mean)\b': "AVG",
            r'\b(count|number\s+of|how\s+many)\b': "COUNT",
            r'\b(maximum|max|highest)\b': "MAX",
            r'\b(minimum|min|lowest)\b': "MIN",
            r'\b(المجموع|الإجمالي)\b': "SUM",
            r'\b(المتوسط)\b': "AVG",
            r'\b(عدد|كم)\b': "COUNT",
        }
        
        # Continuation patterns
        self.continuation_patterns = {
            r'^(and|also|additionally)\b': "add_to_previous",
            r'^(but|however|except)\b': "modify_previous",
            r'^(more|show\s+more|more\s+details?)\b': "expand_previous",
            r'^(same\s+but|like\s+that\s+but)\b': "similar_modified",
            r'^(وأيضا|بالإضافة)\b': "add_to_previous",
        }
    
    def resolve_references(
        self,
        query: str,
        context: Optional[ConversationContext] = None
    ) -> Tuple[str, List[ResolvedReference]]:
        """
        Resolve all references in a query.
        
        Args:
            query: The user's query with potential references
            context: Optional conversation context (uses internal if not provided)
            
        Returns:
            Tuple of (resolved_query, list of resolved references)
        """
        if context:
            self.context = context
        
        resolved_refs = []
        resolved_query = query
        
        # Process each type of reference
        resolved_query, temporal_refs = self._resolve_temporal(resolved_query)
        resolved_refs.extend(temporal_refs)
        
        resolved_query, quant_refs = self._resolve_quantitative(resolved_query)
        resolved_refs.extend(quant_refs)
        
        resolved_query, breakdown_refs = self._resolve_breakdown(resolved_query)
        resolved_refs.extend(breakdown_refs)
        
        resolved_query, entity_refs = self._resolve_entity(resolved_query)
        resolved_refs.extend(entity_refs)
        
        resolved_query, filter_refs = self._resolve_filters(resolved_query)
        resolved_refs.extend(filter_refs)
        
        resolved_query, agg_refs = self._resolve_aggregation(resolved_query)
        resolved_refs.extend(agg_refs)
        
        if resolved_refs:
            logger.info(f"Resolved {len(resolved_refs)} references in query")
        
        return resolved_query, resolved_refs
    
    def update_context(
        self,
        time_period: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_value: Optional[str] = None,
        aggregation: Optional[str] = None,
        metric: Optional[str] = None,
        breakdown: Optional[str] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None
    ):
        """Update conversation context with new information"""
        if time_period:
            self.context.last_time_period = time_period
        if entity_type:
            self.context.last_entity_type = entity_type
        if entity_value:
            self.context.last_entity_value = entity_value
            if entity_type:
                self.context.mentioned_entities[entity_type] = entity_value
        if aggregation:
            self.context.last_aggregation = aggregation
        if metric:
            self.context.last_metric = metric
        if breakdown:
            self.context.last_breakdown = breakdown
        if limit:
            self.context.last_limit = limit
        if query:
            self.context.query_history.append(query)
            # Keep only last 10 queries
            self.context.query_history = self.context.query_history[-10:]
    
    def get_sql_components(
        self,
        resolved_refs: List[ResolvedReference]
    ) -> Dict[str, List[str]]:
        """
        Extract SQL components from resolved references.
        
        Returns:
            Dict with keys: 'select', 'where', 'group_by', 'order_by', 'limit'
        """
        components = {
            'select': [],
            'where': [],
            'group_by': [],
            'order_by': [],
            'limit': []
        }
        
        for ref in resolved_refs:
            if ref.sql_select:
                components['select'].append(ref.sql_select)
            if ref.sql_where:
                components['where'].append(ref.sql_where)
            if ref.sql_group_by:
                components['group_by'].append(ref.sql_group_by)
            if ref.sql_order_by:
                components['order_by'].append(ref.sql_order_by)
            if ref.sql_limit:
                components['limit'].append(ref.sql_limit)
        
        return components
    
    def reset_context(self):
        """Reset conversation context"""
        self.context = ConversationContext()
    
    # =========================================================================
    # Private resolution methods
    # =========================================================================
    
    def _resolve_temporal(self, query: str) -> Tuple[str, List[ResolvedReference]]:
        """Resolve temporal references"""
        resolved = []
        modified_query = query
        
        for pattern, resolver in self.temporal_patterns.items():
            matches = list(re.finditer(pattern, query, re.IGNORECASE))
            for match in matches:
                try:
                    if callable(resolver):
                        # Check if resolver expects match parameter
                        import inspect
                        sig = inspect.signature(resolver)
                        if len(sig.parameters) > 1:
                            value = resolver(self.context, match)
                        else:
                            value = resolver(self.context)
                    else:
                        value = resolver
                    
                    # Generate SQL fragment based on resolved value
                    sql_where = self._temporal_to_sql(value)
                    
                    resolved.append(ResolvedReference(
                        original_text=match.group(0),
                        reference_type=ReferenceType.TEMPORAL,
                        resolved_value=value,
                        sql_where=sql_where
                    ))
                    
                    # Update query with resolved value
                    if isinstance(value, int):  # Year
                        modified_query = modified_query.replace(match.group(0), str(value))
                    elif isinstance(value, tuple) and len(value) == 2:  # (year, month) or (year, quarter)
                        modified_query = modified_query.replace(match.group(0), f"{value[0]}-{value[1]:02d}")
                        
                except Exception as e:
                    logger.warning(f"Failed to resolve temporal reference '{match.group(0)}': {e}")
        
        return modified_query, resolved
    
    def _resolve_quantitative(self, query: str) -> Tuple[str, List[ResolvedReference]]:
        """Resolve quantitative references like 'top 5', 'bottom 10'"""
        resolved = []
        modified_query = query
        
        for pattern, resolver in self.quantitative_patterns.items():
            matches = list(re.finditer(pattern, query, re.IGNORECASE))
            for match in matches:
                try:
                    order_dir, limit = resolver(match)
                    
                    resolved.append(ResolvedReference(
                        original_text=match.group(0),
                        reference_type=ReferenceType.QUANTITATIVE,
                        resolved_value={"order": order_dir, "limit": limit},
                        sql_order_by=order_dir,
                        sql_limit=f"TOP {limit}"
                    ))
                    
                    # Update context
                    self.context.last_limit = limit
                    
                except Exception as e:
                    logger.warning(f"Failed to resolve quantitative reference '{match.group(0)}': {e}")
        
        return modified_query, resolved
    
    def _resolve_breakdown(self, query: str) -> Tuple[str, List[ResolvedReference]]:
        """Resolve breakdown references"""
        resolved = []
        modified_query = query
        
        for pattern, breakdown_type in self.breakdown_patterns.items():
            matches = list(re.finditer(pattern, query, re.IGNORECASE))
            for match in matches:
                try:
                    sql_group_by = self._breakdown_to_sql(breakdown_type)
                    
                    resolved.append(ResolvedReference(
                        original_text=match.group(0),
                        reference_type=ReferenceType.BREAKDOWN,
                        resolved_value=breakdown_type,
                        sql_group_by=sql_group_by
                    ))
                    
                    # Update context
                    self.context.last_breakdown = breakdown_type
                    
                except Exception as e:
                    logger.warning(f"Failed to resolve breakdown reference '{match.group(0)}': {e}")
        
        return modified_query, resolved
    
    def _resolve_entity(self, query: str) -> Tuple[str, List[ResolvedReference]]:
        """Resolve entity references"""
        resolved = []
        modified_query = query
        
        for pattern, ref_type in self.entity_patterns.items():
            matches = list(re.finditer(pattern, query, re.IGNORECASE))
            for match in matches:
                try:
                    if ref_type in ("same_entity", "last_entity"):
                        # Use last mentioned entity
                        if self.context.last_entity_type and self.context.last_entity_value:
                            entity_type = self.context.last_entity_type
                            entity_value = self.context.last_entity_value
                            sql_where = self._entity_to_sql(entity_type, entity_value)
                            
                            resolved.append(ResolvedReference(
                                original_text=match.group(0),
                                reference_type=ReferenceType.ENTITY,
                                resolved_value={"type": entity_type, "value": entity_value},
                                sql_where=sql_where
                            ))
                            
                            # Replace reference with actual entity name
                            modified_query = modified_query.replace(match.group(0), entity_value)
                            
                except Exception as e:
                    logger.warning(f"Failed to resolve entity reference '{match.group(0)}': {e}")
        
        return modified_query, resolved
    
    def _resolve_filters(self, query: str) -> Tuple[str, List[ResolvedReference]]:
        """Resolve filter references"""
        resolved = []
        modified_query = query
        
        for pattern, filter_info in self.filter_patterns.items():
            matches = list(re.finditer(pattern, query, re.IGNORECASE))
            for match in matches:
                try:
                    if isinstance(filter_info, tuple):
                        filter_type, filter_value = filter_info
                        sql_where = self._filter_to_sql(filter_type, filter_value)
                        
                        resolved.append(ResolvedReference(
                            original_text=match.group(0),
                            reference_type=ReferenceType.FILTER,
                            resolved_value={"type": filter_type, "value": filter_value},
                            sql_where=sql_where
                        ))
                        
                except Exception as e:
                    logger.warning(f"Failed to resolve filter reference '{match.group(0)}': {e}")
        
        return modified_query, resolved
    
    def _resolve_aggregation(self, query: str) -> Tuple[str, List[ResolvedReference]]:
        """Resolve aggregation references"""
        resolved = []
        modified_query = query
        
        for pattern, agg_type in self.aggregation_patterns.items():
            matches = list(re.finditer(pattern, query, re.IGNORECASE))
            for match in matches:
                try:
                    resolved.append(ResolvedReference(
                        original_text=match.group(0),
                        reference_type=ReferenceType.AGGREGATION,
                        resolved_value=agg_type,
                        sql_select=agg_type
                    ))
                    
                    # Update context
                    self.context.last_aggregation = agg_type
                    
                except Exception as e:
                    logger.warning(f"Failed to resolve aggregation reference '{match.group(0)}': {e}")
        
        return modified_query, resolved
    
    # =========================================================================
    # SQL generation helpers
    # =========================================================================
    
    def _temporal_to_sql(self, value: Any) -> str:
        """Convert temporal value to SQL WHERE clause"""
        if isinstance(value, int):
            # Year
            return f"YEAR(e.SubmitionDate) = {value}"
        elif isinstance(value, tuple):
            if len(value) == 2:
                year, part = value
                if part <= 12:  # Month
                    return f"YEAR(e.SubmitionDate) = {year} AND MONTH(e.SubmitionDate) = {part}"
                elif part <= 4:  # Quarter
                    quarter_months = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
                    start, end = quarter_months.get(part, (1, 3))
                    return f"YEAR(e.SubmitionDate) = {year} AND MONTH(e.SubmitionDate) BETWEEN {start} AND {end}"
            elif len(value) == 4:  # Date range (year, month, day_start, day_end)
                year, month, day_start, day_end = value
                return f"e.SubmitionDate BETWEEN '{year}-{month:02d}-{day_start:02d}' AND '{year}-{month:02d}-{day_end:02d}'"
        elif value == "YOY":
            year = self.context.current_year
            return f"YEAR(e.SubmitionDate) IN ({year}, {year - 1})"
        elif value == "MOM":
            year, month = self.context.current_year, self.context.current_month
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            return f"(YEAR(e.SubmitionDate) = {year} AND MONTH(e.SubmitionDate) = {month}) OR (YEAR(e.SubmitionDate) = {prev_year} AND MONTH(e.SubmitionDate) = {prev_month})"
        
        return ""
    
    def _breakdown_to_sql(self, breakdown_type: str) -> str:
        """Convert breakdown type to SQL GROUP BY clause"""
        mappings = {
            "Location": "l.Name, l.Id",
            "Neighborhood": "n.Name, n.Id",
            "Inspector": "u.Name, u.Id",
            "Month": "FORMAT(e.SubmitionDate, 'yyyy-MM')",
            "Week": "DATEPART(YEAR, e.SubmitionDate), DATEPART(WEEK, e.SubmitionDate)",
            "Day": "CAST(e.SubmitionDate AS DATE)",
            "Quarter": "YEAR(e.SubmitionDate), DATEPART(QUARTER, e.SubmitionDate)",
            "ViolationType": "vt.Name, vt.Id",
            "Category": "vc.Name, vc.Id",
            "breakdown_required": self.context.last_breakdown or "l.Name"
        }
        return mappings.get(breakdown_type, breakdown_type)
    
    def _entity_to_sql(self, entity_type: str, entity_value: str) -> str:
        """Convert entity reference to SQL WHERE clause"""
        mappings = {
            "inspector": f"u.Name LIKE '%{entity_value}%'",
            "location": f"l.Name LIKE '%{entity_value}%'",
            "neighborhood": f"n.Name LIKE '%{entity_value}%'",
            "violation_type": f"vt.Name LIKE '%{entity_value}%'",
        }
        return mappings.get(entity_type.lower(), f"1=1")
    
    def _filter_to_sql(self, filter_type: str, filter_value: Any) -> str:
        """Convert filter to SQL WHERE clause"""
        if filter_type == "RiskLevel":
            return f"risk_level = '{filter_value}'"
        elif filter_type == "HasViolations":
            return "violation_count > 0" if filter_value else "violation_count = 0"
        elif filter_type == "IsCompliant":
            return "e.Score >= 80" if filter_value else "e.Score < 80"
        return ""
    
    # =========================================================================
    # Temporal calculation helpers
    # =========================================================================
    
    def _get_last_month(self, ctx: ConversationContext) -> Tuple[int, int]:
        """Get last month as (year, month) tuple"""
        month = ctx.current_month - 1
        year = ctx.current_year
        if month == 0:
            month = 12
            year -= 1
        return (year, month)
    
    def _get_last_week(self) -> Tuple[int, int, int, int]:
        """Get last week as date range"""
        today = datetime.now()
        last_week_end = today - timedelta(days=today.weekday() + 1)
        last_week_start = last_week_end - timedelta(days=6)
        return (last_week_start.year, last_week_start.month, 
                last_week_start.day, last_week_end.day)
    
    def _get_this_week(self) -> Tuple[int, int, int, int]:
        """Get this week as date range"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        return (week_start.year, week_start.month, week_start.day, today.day)
    
    def _get_last_quarter(self, ctx: ConversationContext) -> Tuple[int, int]:
        """Get last quarter as (year, quarter) tuple"""
        current_quarter = (ctx.current_month - 1) // 3 + 1
        if current_quarter == 1:
            return (ctx.current_year - 1, 4)
        return (ctx.current_year, current_quarter - 1)
    
    def _get_current_quarter(self, ctx: ConversationContext) -> Tuple[int, int]:
        """Get current quarter as (year, quarter) tuple"""
        current_quarter = (ctx.current_month - 1) // 3 + 1
        return (ctx.current_year, current_quarter)
    
    def _same_period_last_year(self, ctx: ConversationContext) -> str:
        """Get same period last year for comparison"""
        return "SAME_PERIOD_LAST_YEAR"


# Singleton instance
_resolver: Optional[ReferenceResolver] = None


def get_reference_resolver() -> ReferenceResolver:
    """Get or create the global reference resolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = ReferenceResolver()
    return _resolver
