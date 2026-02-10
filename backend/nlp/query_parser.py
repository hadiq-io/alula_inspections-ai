"""
Query Parser - Claude-powered NL to structured query extraction
===============================================================
Uses Claude Sonnet 4.5 to extract intent, entities, filters, and 
optimal chart type from natural language queries in Arabic or English.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class QueryParser:
    """
    Parses natural language queries using Claude Sonnet 4.5.
    Extracts structured information for SQL generation.
    """
    
    def __init__(
        self,
        azure_endpoint: str = None,
        azure_api_key: str = None
    ):
        self.endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = azure_api_key or os.getenv("AZURE_OPENAI_KEY")
        self.model = "claude-sonnet-4-5"
        
    def get_extraction_prompt(self) -> str:
        """System prompt for structured entity extraction"""
        return """You are an expert query parser for the AlUla Municipal Inspection System.
Your task is to extract structured information from natural language queries about inspections, violations, compliance, and reports.

## CRITICAL: DISAMBIGUATION RULES
Before parsing, carefully distinguish between these commonly confused terms:

1. **INSPECTORS vs INSPECTIONS**
   - "Inspectors" = People (who/which inspector, inspector performance, inspector list)
   - "Inspections" = Events (how many, when, inspection results)
   - If ambiguous, set "needs_clarification": true
   
2. **EVENTS vs INSPECTIONS** 
   - In this system, "Event" = Inspection (they are the same thing)
   - Event table contains inspection records
   
3. **LOCATIONS vs NEIGHBORHOODS**
   - Database has individual business "Locations" (restaurants, shops)
   - There is NO neighborhoods table - locations are individual businesses
   - If user asks about "neighborhoods" or "areas", flag as needs_clarification

4. **UNKNOWN CONCEPTS** - Set "needs_clarification": true for:
   - "Health Certificates" - not in database
   - "Permits" - not in database  
   - "Licenses" - not in database
   - Generic terms that don't map to tables

## DATABASE REALITY:
Tables available: Event (inspections), Locations (businesses), EventViolation (violations), Activity, ML_* tables
- Inspector data is in Event.AssignTo field (user IDs, not names)
- Locations are businesses, not geographic areas

## ENTITY EXTRACTION RULES:

### Metrics (what is being measured):
- violations / المخالفات - violation counts, values, severity
- compliance / الامتثال - compliance scores, rates
- inspections / التفتيش / الفحوصات - inspection counts (Event table)
- inspectors / المفتشين - inspector data (Event.AssignTo)
- reports / البلاغات - report counts, status
- performance / الأداء - inspector or location performance
- locations / المواقع - business locations

### Time Periods:
- Extract year (2023, 2024, 2025, etc.)
- Extract month if specified (January/يناير, etc.)
- Extract quarter if specified (Q1/الربع الأول, etc.)
- "last year" / "السنة الماضية" = 2025
- "this year" / "هذه السنة" = 2026
- "last month" / "الشهر الماضي" = January 2026

### Status:
- open/مفتوح, closed/مغلق, pending/معلق
- valid/صالح, expired/منتهي (for licenses)

## INTENT CLASSIFICATION:
- COUNT: How many? / كم عدد؟
- SUM: Total value? / المجموع؟
- AVERAGE: Average/mean? / المتوسط؟
- RANKING: Top/best/worst N? / أفضل/أسوأ؟
- COMPARISON: Compare X vs Y? / مقارنة؟
- TREND: Over time? Monthly? / الاتجاه؟
- FORECAST: Predict/expect? / التوقع؟
- FILTER: Specific subset? / تصفية؟
- DETAIL: Show details? / التفاصيل؟
- LIST: List all? / قائمة؟
- MAP: Show on map? Location visualization? / عرض على الخريطة؟

## CONFIDENCE SCORING:
Assign a confidence score (0.0 to 1.0):
- 1.0: Clear, unambiguous query that maps directly to data
- 0.7-0.9: Mostly clear, minor assumptions made  
- 0.5-0.6: Ambiguous, could have multiple interpretations
- <0.5: Very unclear, likely needs clarification

## OUTPUT FORMAT:
Return ONLY valid JSON (no markdown, no explanation):
{
  "language": "ar" or "en",
  "intent": "COUNT|SUM|AVERAGE|RANKING|COMPARISON|TREND|FORECAST|FILTER|DETAIL|LIST|MAP",
  "metric": "violations|compliance|inspections|inspectors|reports|performance|locations",
  "entities": {
    "location": "name or null",
    "activity": "type or null",
    "inspector_id": "id or null",
    "status": "status or null",
    "severity": "level or null"
  },
  "time_period": {
    "year": 2024 or null,
    "month": 1-12 or null,
    "quarter": 1-4 or null
  },
  "limit": number or null,
  "chart_type": "bar|line|pie|area|composed|map|none",
  "chart_rationale": "brief explanation of chart choice",
  "confidence": 0.0 to 1.0,
  "needs_clarification": true or false,
  "clarification_reason": "explanation if clarification needed, or null"
}
"""

    def parse(self, query: str, context: Optional[list] = None) -> Dict[str, Any]:
        """
        Parse a natural language query into structured format.
        
        Args:
            query: The user's natural language query
            context: Optional previous conversation turns for follow-up handling
            
        Returns:
            Structured query dict with intent, entities, chart_type, etc.
        """
        try:
            url = f"{self.endpoint}/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Build messages with context for follow-ups
            messages = []
            if context:
                for turn in context[-4:]:  # Last 4 turns for context
                    messages.append(turn)
            
            messages.append({
                "role": "user",
                "content": f"Parse this query and extract structured information:\n\n\"{query}\""
            })
            
            payload = {
                "model": self.model,
                "max_tokens": 1000,
                "system": self.get_extraction_prompt(),
                "messages": messages
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Parse error: {response.status_code}")
                return self._fallback_parse(query)
            
            result = response.json()
            text = result.get('content', [{}])[0].get('text', '{}')
            
            # Clean JSON response
            text = text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1].rsplit('```', 1)[0]
            
            parsed = json.loads(text)
            print(f"✅ Parsed: {parsed.get('intent')} | {parsed.get('metric')} | Chart: {parsed.get('chart_type')}")
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            return self._fallback_parse(query)
        except Exception as e:
            print(f"❌ Parse exception: {e}")
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Fallback parsing when Claude fails - basic keyword matching"""
        query_lower = query.lower()
        
        # Detect language
        is_arabic = any('\u0600' <= c <= '\u06FF' for c in query)
        language = 'ar' if is_arabic else 'en'
        
        # Basic intent detection
        intent = 'COUNT'
        if any(w in query_lower for w in ['trend', 'monthly', 'شهري', 'اتجاه']):
            intent = 'TREND'
        elif any(w in query_lower for w in ['top', 'best', 'worst', 'أفضل', 'أسوأ']):
            intent = 'RANKING'
        elif any(w in query_lower for w in ['average', 'mean', 'متوسط']):
            intent = 'AVERAGE'
        elif any(w in query_lower for w in ['compare', 'مقارنة']):
            intent = 'COMPARISON'
        elif any(w in query_lower for w in ['forecast', 'predict', 'توقع']):
            intent = 'FORECAST'
            
        # Basic metric detection
        metric = 'violations'
        if any(w in query_lower for w in ['compliance', 'امتثال', 'score']):
            metric = 'compliance'
        elif any(w in query_lower for w in ['inspection', 'تفتيش', 'فحص']):
            metric = 'inspections'
        elif any(w in query_lower for w in ['report', 'بلاغ']):
            metric = 'reports'
        
        # Extract year from query (2020-2099)
        import re
        year_match = re.search(r'\b(20[2-9][0-9])\b', query)
        year = int(year_match.group(1)) if year_match else None
            
        # Chart type based on intent
        chart_map = {
            'TREND': 'line',
            'RANKING': 'bar',
            'COUNT': 'bar',
            'AVERAGE': 'bar',
            'COMPARISON': 'bar',
            'FORECAST': 'line',
            'MAP': 'map',
            'SPATIAL': 'map'
        }
        
        return {
            "language": language,
            "intent": intent,
            "metric": metric,
            "entities": {
                "neighborhood": None,
                "activity": None,
                "inspector": None,
                "status": None,
                "severity": None
            },
            "time_range": {
                "year": year,
                "month": None,
                "quarter": None
            },
            "limit": 10,
            "chart_type": chart_map.get(intent, 'bar'),
            "chart_rationale": "Fallback: default chart for intent"
        }

    def detect_language(self, text: str) -> str:
        """Detect if text is Arabic or English"""
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        return 'ar' if arabic_chars > len(text) * 0.3 else 'en'
