"""
SQL Mapper Module
=================
Maps parsed user queries to SQL templates and builds executable queries.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .sql_templates import ALL_TEMPLATES


class SQLMapper:
    """
    Maps parsed NL queries to SQL templates and builds executable queries.
    Uses semantic matching based on intent and entities.
    """
    
    def __init__(self):
        self.templates = ALL_TEMPLATES
        self.default_limit = 10
        self.default_year = datetime.now().year
        
        # Intent to template domain mapping
        self.intent_domain_map = {
            "COUNT": ["reports", "violations", "inspectors", "neighborhoods"],
            "SUM": ["violations"],
            "AVERAGE": ["reports", "violations", "inspectors", "neighborhoods"],
            "RANKING": ["violations", "inspectors", "neighborhoods", "complex"],
            "COMPARISON": ["violations", "neighborhoods", "complex"],
            "TREND": ["reports", "violations", "inspectors", "neighborhoods"],
            "FORECAST": ["forecasting"],
            "FILTER": ["reports", "violations", "neighborhoods", "forecasting"],
            "DETAIL": ["inspectors", "neighborhoods", "complex"],
            "MAP": ["map", "spatial", "location", "geography"],
            "SPATIAL": ["map", "spatial", "location", "geography"]
        }
        
        # Entity to template mapping (for quick lookup)
        self.entity_template_map = self._build_entity_map()
    
    def _build_entity_map(self) -> Dict[str, List[str]]:
        """Build a reverse mapping from entities to template IDs."""
        entity_map = {}
        
        for template_id, template in self.templates.items():
            # Extract entities from template SQL
            sql = template.get("sql", "").lower()
            
            # Add to entity groups
            if "eventviolation" in sql or "violation" in template_id.lower():
                entity_map.setdefault("metric:violations", []).append(template_id)
            if "event" in sql and "eventviolation" not in sql:
                entity_map.setdefault("metric:inspections", []).append(template_id)
            if "reporterid" in sql or "inspector" in template_id.lower():
                entity_map.setdefault("inspector", []).append(template_id)
            if "neighborhoodname" in sql or "neighborhood" in template_id.lower():
                entity_map.setdefault("neighborhood", []).append(template_id)
            if "ml_" in sql or "forecast" in template_id.lower():
                entity_map.setdefault("metric:predictions", []).append(template_id)
            if "score" in sql:
                entity_map.setdefault("metric:score", []).append(template_id)
            if "locationtype" in sql or "activity" in template_id.lower():
                entity_map.setdefault("activity", []).append(template_id)
        
        return entity_map
    
    def map(self, parsed: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Map a parsed query to a SQL template.
        
        Args:
            parsed: Output from QueryParser containing intent, entities, time_range, etc.
            
        Returns:
            Tuple of (template_id, template_data)
        """
        intent = parsed.get("intent", "COUNT")
        entities = parsed.get("entities", {})
        metric = parsed.get("metric")  # Get metric from top-level
        time_range = parsed.get("time_range") or parsed.get("time_period", {})
        
        # Score each template
        scored_templates = []
        
        for template_id, template in self.templates.items():
            score = self._calculate_template_score(template, intent, entities, time_range, metric)
            if score > 0:
                scored_templates.append((template_id, template, score))
        
        # Sort by score descending
        scored_templates.sort(key=lambda x: x[2], reverse=True)
        
        if not scored_templates:
            # Fallback to a default template
            return self._get_fallback_template(intent, entities)
        
        best_template_id, best_template, _ = scored_templates[0]
        return best_template_id, best_template
    
    def _calculate_template_score(
        self, 
        template: Dict[str, Any], 
        intent: str,
        entities: Dict[str, Any],
        time_range: Dict[str, Any],
        metric: Optional[str] = None
    ) -> float:
        """Calculate a match score for a template based on parsed query."""
        score = 0.0
        template_id = template.get("id", "").upper()
        sql = template.get("sql", "").lower()
        
        # Intent match (most important)
        template_intents = template.get("intents", [])
        if intent in template_intents:
            score += 10.0
        elif any(i in template_intents for i in self.intent_domain_map.get(intent, [])):
            score += 5.0
        
        # MAP/SPATIAL intent - Strong boost for MAP templates
        if intent in ("MAP", "SPATIAL", "GEOGRAPHY", "LOCATION"):
            if template_id.startswith("MAP_"):
                score += 30.0  # Very high priority for map templates
            elif template.get("default_chart") == "map":
                score += 25.0
        
        # ==================== ENTITY MATCHING ====================
        
        # Inspector entity - ENHANCED MATCHING
        if entities.get("inspector"):
            # Strong match: Template is specifically for inspectors
            if template_id.startswith("INS_"):
                score += 20.0  # Very high priority for inspector templates
            elif "reporterid" in sql or "inspector" in template_id.lower():
                score += 10.0
            # Moderate match: SQL mentions reporter
            elif "reporter" in sql:
                score += 5.0
        
        # Location/Neighborhood entity - ENHANCED MATCHING
        if entities.get("neighborhood") or entities.get("location"):
            # Strong match: Template is specifically for locations/neighborhoods
            if template_id.startswith("LOC_"):
                score += 20.0  # Very high priority for location templates
            elif "neighborhood" in template_id.lower() or "location" in template_id.lower():
                score += 15.0
            # Check SQL for location references
            elif "l.name" in sql or "locations" in sql or "location" in sql:
                score += 10.0
            elif "neighborhoodname" in sql:
                score += 8.0
        
        # Activity entity - ENHANCED MATCHING for sector/activity filtering
        if entities.get("activity"):
            # If activity is specified and template has activity filter capability
            if "activity_filter" in template.get("filters", {}):
                score += 25.0  # Strong boost for templates with activity filters
            if "locationtype" in sql or "activity" in template_id.lower():
                score += 15.0
            # If looking for violations by activity, prioritize VIO_13
            if template_id == "VIO_13":
                score += 30.0  # Highest priority for violations_by_activity_type
        
        # ==================== METRIC MATCHING ====================
        
        if metric:
            metric_lower = metric.lower()
            
            # Violations metric
            if metric_lower in ("violations", "violation", "مخالفات", "مخالفة"):
                if template_id.startswith("VIO_"):
                    score += 25.0  # Highest priority for violation templates
                elif "eventviolation" in sql:
                    score += 15.0  # Strong preference for violations queries
                elif "violation" in template_id.lower():
                    score += 12.0
                else:
                    score -= 10.0  # Penalize non-violation templates
            
            # Inspections metric
            elif metric_lower in ("inspections", "inspection", "events", "فحوصات", "تفتيش"):
                if template_id.startswith("RPT_"):
                    score += 15.0  # Reports templates for inspections
                elif "event" in sql and "eventviolation" not in sql:
                    score += 10.0
            
            # Inspector performance metric
            elif metric_lower in ("inspectors", "inspector", "performance", "أداء", "مفتشين"):
                if template_id.startswith("INS_"):
                    score += 25.0
                elif "reporterid" in sql:
                    score += 10.0
            
            # Score/compliance metric
            elif metric_lower in ("score", "compliance", "امتثال", "درجة"):
                if "score" in sql:
                    score += 10.0
                elif "status" in sql:
                    score += 5.0
            
            # Forecast/prediction metric
            elif metric_lower in ("forecast", "prediction", "trend", "توقعات", "اتجاه"):
                if template_id.startswith("FRC_"):
                    score += 20.0
        
        # ==================== TIME RANGE MATCHING ====================
        
        if time_range.get("year"):
            if "year" in template.get("filters", {}) or "year" in sql:
                score += 2.0
        
        if time_range.get("month"):
            if "month" in sql:
                score += 3.0
        
        # ==================== KEYWORD MATCHING ====================
        
        # Top/ranking queries - prefer templates with ranking logic
        if intent == "RANKING":
            if "order by" in sql and ("desc" in sql or "top" in sql):
                score += 5.0
        
        # Trend queries
        if intent == "TREND":
            if "group by" in sql and ("month" in sql or "year" in sql):
                score += 5.0
        
        return score
    
    def _get_fallback_template(
        self, 
        intent: str, 
        entities: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Return a reasonable fallback template when no good match is found."""
        
        # Check for common entities
        if entities.get("neighborhood"):
            return "neighborhood_inspection_count", self.templates.get(
                "neighborhood_inspection_count", 
                self._generic_count_template()
            )
        
        if entities.get("inspector"):
            return "inspector_inspections_count", self.templates.get(
                "inspector_inspections_count",
                self._generic_count_template()
            )
        
        # Intent-based fallbacks
        if intent == "RANKING":
            return "neighborhood_best_compliance", self.templates.get(
                "neighborhood_best_compliance",
                self._generic_count_template()
            )
        
        if intent == "TREND":
            return "reports_monthly_trend", self.templates.get(
                "reports_monthly_trend",
                self._generic_count_template()
            )
        
        if intent == "FORECAST":
            return "forecast_inspections", self.templates.get(
                "forecast_inspections",
                self._generic_count_template()
            )
        
        # Default: report count
        return "reports_by_status", self.templates.get(
            "reports_by_status",
            self._generic_count_template()
        )
    
    def _generic_count_template(self) -> Dict[str, Any]:
        """Return a generic count template as final fallback."""
        return {
            "id": "GEN_01",
            "intents": ["COUNT"],
            "default_chart": "none",
            "sql": """
                SELECT 
                    COUNT(*) as total_count
                FROM Event e
                WHERE e.IsDeleted = 0
                  {year_filter}
            """,
            "filters": {
                "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
            }
        }
    
    def build_query(
        self, 
        template_id: str,
        template: Dict[str, Any], 
        parsed: Dict[str, Any]
    ) -> str:
        """
        Build an executable SQL query from a template.
        
        Args:
            template_id: The template identifier
            template: The template data
            parsed: The parsed query with entities and time_range
            
        Returns:
            Executable SQL query string
        """
        sql = template.get("sql", "")
        filters = template.get("filters", {})
        entities = parsed.get("entities", {})
        # Support both time_range and time_period field names
        time_range = parsed.get("time_range") or parsed.get("time_period", {})
        
        # Build filter clauses
        active_filters = {}
        
        # Year filter - only apply if year is specified
        year = time_range.get("year")
        if year and "year_filter" in filters:
            active_filters["year_filter"] = filters["year_filter"].format(year=year)
        elif not year and "year_filter" in filters:
            # If no year specified, remove the year filter entirely
            pass  # Don't add to active_filters, will be replaced with empty string
        
        # Neighborhood filter
        neighborhood = entities.get("neighborhood")
        if neighborhood and "neighborhood_filter" in filters:
            # Escape single quotes for SQL safety
            safe_neighborhood = neighborhood.replace("'", "''")
            active_filters["neighborhood_filter"] = filters["neighborhood_filter"].format(
                neighborhood=safe_neighborhood
            )
        
        # Inspector filter
        inspector_id = entities.get("inspector")
        if inspector_id and "inspector_filter" in filters:
            active_filters["inspector_filter"] = filters["inspector_filter"].format(
                inspector_id=inspector_id
            )
        
        # Activity filter - normalize Arabic by stripping definite article "ال"
        activity = entities.get("activity")
        if activity and "activity_filter" in filters:
            safe_activity = activity.replace("'", "''")
            # Strip Arabic definite article "ال" from the beginning if present
            if safe_activity.startswith("ال"):
                safe_activity = safe_activity[2:]  # Remove "ال" prefix
            active_filters["activity_filter"] = filters["activity_filter"].format(
                activity=safe_activity
            )
        
        # Severity filter
        severity = entities.get("severity")
        if severity and "severity_filter" in filters:
            active_filters["severity_filter"] = filters["severity_filter"].format(
                severity=severity
            )
        
        # Apply filters to SQL
        for filter_name in filters.keys():
            placeholder = "{" + filter_name + "}"
            if filter_name in active_filters:
                sql = sql.replace(placeholder, active_filters[filter_name])
            else:
                sql = sql.replace(placeholder, "")
        
        # Replace remaining placeholders
        if year:
            sql = sql.replace("{year}", str(year))
        else:
            # Remove remaining year placeholders if no year specified
            sql = sql.replace("{year}", str(self.default_year))
        sql = sql.replace("{limit}", str(entities.get("limit", self.default_limit)))
        
        # Handle neighborhood placeholder in non-filter context
        if neighborhood:
            safe_neighborhood = neighborhood.replace("'", "''")
            sql = sql.replace("{neighborhood}", safe_neighborhood)
        
        # Handle inspector_id placeholder
        if inspector_id:
            sql = sql.replace("{inspector_id}", str(inspector_id))
        
        # Clean up the SQL
        sql = self._clean_sql(sql)
        
        return sql
    
    def _clean_sql(self, sql: str) -> str:
        """Clean up the SQL query by removing extra whitespace and newlines."""
        # Remove excessive whitespace
        sql = re.sub(r'\s+', ' ', sql)
        # Remove leading/trailing whitespace
        sql = sql.strip()
        # Clean up around keywords
        sql = re.sub(r'\s+,', ',', sql)
        sql = re.sub(r',\s+', ', ', sql)
        # Remove empty AND/OR clauses
        sql = re.sub(r'\s+AND\s+AND\s+', ' AND ', sql, flags=re.IGNORECASE)
        sql = re.sub(r'WHERE\s+AND\s+', 'WHERE ', sql, flags=re.IGNORECASE)
        sql = re.sub(r'AND\s+ORDER', ' ORDER', sql, flags=re.IGNORECASE)
        sql = re.sub(r'AND\s+GROUP', ' GROUP', sql, flags=re.IGNORECASE)
        sql = re.sub(r'AND\s+HAVING', ' HAVING', sql, flags=re.IGNORECASE)
        
        return sql
    
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific template."""
        return self.templates.get(template_id)
    
    def search_templates(
        self, 
        query_ar: Optional[str] = None,
        query_en: Optional[str] = None,
        intent: Optional[str] = None
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search templates by Arabic/English keywords or intent.
        
        Returns:
            List of (template_id, template, score) tuples sorted by relevance
        """
        results = []
        
        for template_id, template in self.templates.items():
            score = 0.0
            
            # Match by Arabic question
            if query_ar:
                template_ar = template.get("question_ar", "").lower()
                if query_ar.lower() in template_ar:
                    score += 5.0
            
            # Match by English question
            if query_en:
                template_en = template.get("question_en", "").lower()
                if query_en.lower() in template_en:
                    score += 5.0
            
            # Match by intent
            if intent:
                if intent in template.get("intents", []):
                    score += 3.0
            
            if score > 0:
                results.append((template_id, template, score))
        
        results.sort(key=lambda x: x[2], reverse=True)
        return results
    
    def get_all_template_ids(self) -> List[str]:
        """Return all available template IDs."""
        return list(self.templates.keys())
    
    def get_template_count(self) -> int:
        """Return the total number of templates."""
        return len(self.templates)
