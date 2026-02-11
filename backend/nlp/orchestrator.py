"""
Intelligent Orchestrator System
===============================
Uses Claude Sonnet 4.5 as the primary reasoning engine to:
1. Analyze and classify every user question
2. Determine if database data is needed
3. Ask clarifying questions when ambiguous
4. Route to appropriate response path

This is the BRAIN of the chatbot - Claude decides what to do, not pattern matching.
"""

import os
import json
import uuid
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class IntelligentOrchestrator:
    """
    Claude-first orchestrator that intelligently routes user questions.
    
    Routes:
    - Route A: Database query (when we have the data and understand the question)
    - Route B: Clarification needed (when question is ambiguous or missing parameters)
    - Route C: General knowledge (when question is outside database scope)
    """
    
    def __init__(self, db_connection=None):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.model = "claude-sonnet-4-5"
        self.db = db_connection
        
        # Session state for tracking clarifications
        self.pending_clarifications: Dict[str, Dict[str, Any]] = {}
        
        # Database schema context for Claude
        self.schema_context = self._build_schema_context()
        
        print("✅ IntelligentOrchestrator initialized")
    
    def _build_schema_context(self) -> str:
        """Build database schema context for Claude to understand available data."""
        return """
## DATABASE SCHEMA - AlUla Municipal Inspection System

### Core Tables:

**Event** (Inspections table - ~243,000 records)
Columns: Id, Duration, ActivityId, EventType, formId, ReporterID, TenantId, Location, 
         AssignTo, AssignToUnit, Notes, Status, Points, IsDeleted, SubmitionDate, 
         LastUpdateDate, AssignedToSubunitId, ResponsibleUnit, IssueCount, Score, 
         CriticalIssueCount, WorkflowId, long, lat, AssignToRole, SolvedIssues, AssetId
Key columns:
- Id: Unique inspection ID (int)
- SubmitionDate: When inspection was submitted (datetime, data from 2022-2025)
- Score: Compliance score (0-100)
- Status: Current status (numeric: 1,2,3,5,9,10, etc.)
- ReporterID: Inspector who conducted it (numeric ID, links to Reporter table)
- Duration: Time spent (minutes)
- CriticalIssueCount: Number of critical issues found
- Location: Location ID (int, links to Locations.Id)
- IsDeleted: Soft delete flag (0 = active, 1 = deleted)

**EventViolation** (Violations table - ~36,000 records)
Columns: Id, EventId, QuestionId, ViolationValue, NonFinancialViolationsTypeId, PeriodValue, 
         HasObjection, ObjectionStatus, OldViolationValue, Severity, QuestionNameEn, QuestionNameAr,
         CreatedBy, CreatedAt, UpdatedBy, UpdatedAt, EditReason, EditAttachmentPath
- Id: Violation ID (GUID)
- EventId: Links to Event.Id
- ViolationValue: Fine amount in SAR (int)
- Severity: Can be NULL, 0, or other values
- HasObjection: Boolean (1=has objection)
- QuestionId: The question/violation type ID (int)
- QuestionNameEn: Violation type name in English
- QuestionNameAr: Violation type name in Arabic
- NOTE: Use QuestionNameEn or QuestionNameAr to group violations by "type"

**Locations** (Businesses/Sites - ~8,000 records)
Columns: Id, Name, NameAr, ShortCode, ImportanceLevel, Category, LocationType, 
         Lat, Long, beaconName, IsActive, Isdeleted, ParentLocation, AccountId, 
         SubCategory, LocationImage, Address, RedirectionMode, LandMark
Key columns:
- Id: Location ID (int)
- Name: Business name (English, nvarchar)
- NameAr: Business name (Arabic, nvarchar)
- Category: Business category (nvarchar)
- LocationType: Activity type classification (nvarchar, e.g., Restaurant, Shop, Hotel)
- Lat, Long: Geographic coordinates (float)
- Isdeleted: Soft delete flag (NOTE: lowercase 'd')
- IsActive: Whether location is active

**EventStatus** (Status Lookup Table)
Columns: Id, Name, NameAr, IsDeleted, IsActive, IsSystem, UpdateDate
- Id: Status ID (links to Event.Status)
- Name: Status name in Arabic/mixed
- NameAr: Arabic name
Key statuses: 1=اعتماد 1, 2=مغلقة (Closed), 3=اعتماد 2, 4=مرفوضة (Rejected), 5=مكتملة (Completed), 6=تحت الإجراء (In Progress), 9=تم انتهاء فترة الاعتراض

**ML_Inspector_Performance** (Inspector Performance Metrics)
Columns: inspector_id, total_inspections, avg_inspection_score, completion_rate, 
         defect_detection_rate, resolution_rate, performance_score, actual_tier, 
         actual_label, predicted_tier, predicted_label, prediction_confidence
- Use this for inspector rankings and performance queries
- actual_label/predicted_label: 'Excellent', 'Good', 'Average', 'Needs Improvement'
- performance_score: 0-100 scale

**EventType** (Inspection Types)
Columns: Id, NameEn, NameAr
- Links to Event.EventType

### IMPORTANT SQL RULES:
1. Use 'IsDeleted = 0' for Event table (capital D)
2. Use 'Isdeleted = 0' for Locations table (lowercase d)
3. The Locations table has 'LocationType' as a STRING column (not foreign key)
4. Join Event to Locations using: Event.Location = Locations.Id
5. **NO Reporter table exists!** Use Event.ReporterID directly (numeric IDs only)
6. For inspector names/performance, use ML_Inspector_Performance table
7. Date column is 'SubmitionDate' (note the typo - not 'SubmissionDate')
8. Use TOP instead of LIMIT for SQL Server
9. For years, use: YEAR(SubmitionDate) = 2025
10. Join Event.Status to EventStatus.Id for status names

**EventStatus** (Status Lookup)
Columns: Id, Name, NameAr
- Join: Event.Status = EventStatus.Id

### ML Prediction Tables (9 models):
- ML_Predictions: KPI forecasts (kpi_id, date, predicted_value)
- ML_Location_Risk: Risk scores by location (location_id, risk_probability, risk_category)
- ML_Inspector_Performance: Inspector performance tiers (inspector_id, performance_score, predicted_label)
- ML_Anomalies: Unusual inspection patterns (inspection_id, anomaly_probability, anomaly_type)
- ML_Severity_Predictions: Predicted violation severity
- ML_Scheduling_Recommendations: Optimal inspection dates
- ML_Objection_Predictions: Appeal outcome forecasts
- ML_Location_Clusters: Location groupings
- ML_Recurrence_Predictions: Repeat violation likelihood

### Data Availability:
- Years with data: 2022, 2023, 2024, 2025
- All months available
- ~512 unique inspectors (ReporterID)
- ~8,000 business locations
- Activity types: Restaurant, Shop, Hotel, Cafe, Supermarket, etc.

### IMPORTANT - Data that DOES NOT exist:
- Health certificates or medical records
- Permits or licenses
- Employee personal records
- Financial data beyond violation fines
- Geographic neighborhoods (only individual business locations)
- Customer reviews or ratings
- **NO ViolationType or ViolationCategory lookup table** - use EventViolation.QuestionNameEn/QuestionNameAr
- **NO ActivityType lookup table** - Locations.LocationType is numeric only
- **NO QuestionSectionId column** - use QuestionId, QuestionNameEn, QuestionNameAr instead

### COMMON SQL PATTERNS:

**Violations by Severity:**
```sql
SELECT 
    CASE WHEN Severity IS NULL THEN 'Not Specified' ELSE CAST(Severity AS VARCHAR) END as SeverityLevel,
    COUNT(*) as ViolationCount,
    SUM(ViolationValue) as TotalFines
FROM EventViolation
GROUP BY Severity
ORDER BY ViolationCount DESC
```

**Violations by QuestionSectionId (closest to "violation types"):**
```sql
SELECT 
    QuestionSectionId as ViolationCategory,
    COUNT(*) as ViolationCount,
    SUM(ViolationValue) as TotalFines
FROM EventViolation
WHERE QuestionSectionId IS NOT NULL
GROUP BY QuestionSectionId
ORDER BY ViolationCount DESC
```

**Business Activity Types (by LocationType numeric):**
```sql
SELECT 
    l.LocationType as ActivityType,
    COUNT(e.Id) as InspectionCount
FROM Event e
JOIN Locations l ON e.Location = l.Id
WHERE e.IsDeleted = 0
GROUP BY l.LocationType
ORDER BY InspectionCount DESC
```

**Restaurant/Specific Business Search (by Name pattern):**
```sql
SELECT l.Name, l.NameAr, COUNT(e.Id) as InspectionCount, AVG(e.Score) as AvgScore
FROM Event e
JOIN Locations l ON e.Location = l.Id
WHERE e.IsDeleted = 0 
  AND (l.Name LIKE '%restaurant%' OR l.Name LIKE '%مطعم%' OR l.NameAr LIKE '%مطعم%')
GROUP BY l.Id, l.Name, l.NameAr
ORDER BY InspectionCount DESC
```

**Last available month (December 2025 - database ends here):**
```sql
SELECT COUNT(*) as InspectionCount
FROM Event
WHERE IsDeleted = 0 
  AND SubmitionDate >= '2025-12-01' AND SubmitionDate < '2026-01-01'
```

**NOTE:** When user asks for "last month" and today is after Dec 2025, 
use December 2025 as the latest available data period.
"""

    def _get_classification_prompt(self) -> str:
        """System prompt for classifying user questions."""
        return f"""You are an intelligent question classifier for the AlUla Municipal Inspection System chatbot.

Your job is to analyze user questions and determine:
1. What the user is actually asking for
2. Whether our database can answer this question
3. What parameters are needed
4. Whether clarification is required

{self.schema_context}

## AVAILABLE QUERY TYPES

### Inspection Queries
- Total inspections (count, by year, by month, by day)
- Inspections by status (open, closed, pending, completed)
- Inspections by type
- Daily/weekly/monthly inspection trends
- Average inspection duration and scores
- Inspection completion rates

### Violation Queries
- Total violations count
- Violations by severity (1-5 scale)
- Violations by category/section
- Total fines (ViolationValue sum)
- Objection rates and status
- Top violating locations
- Violations by activity type

### Inspector Queries
- Inspector count (unique ReporterID)
- Top inspectors by inspections completed
- Inspector performance scores (from ML table)
- Workload distribution
- Inspector efficiency metrics

### Location Queries
- All locations list
- Locations by category
- Location compliance scores
- High-risk locations (from ML table)
- Location inspection history

### Forecasting/ML Queries
- Predicted inspection volumes
- Risk predictions
- Performance predictions
- Trend analysis

## YOUR TASK

Analyze the user's question and respond with a JSON object:

```json
{{
  "route": "database" | "clarification" | "general",
  "confidence": 0.0 to 1.0,
  "reasoning": "Brief explanation of your classification decision",
  "intent": "What the user wants in plain English",
  "query_type": "inspections" | "violations" | "inspectors" | "locations" | "forecasting" | "general",
  "parameters": {{
    "year": null or number (e.g., 2024),
    "month": null or 1-12,
    "day": null or 1-31,
    "inspector_id": null or number,
    "location_name": null or string,
    "location_id": null or number,
    "activity_type": null or string,
    "status": null or string,
    "severity": null or 1-5,
    "limit": null or number (for top N queries),
    "time_period": null or "daily" | "weekly" | "monthly" | "yearly",
    "date_from": null or "YYYY-MM-DD",
    "date_to": null or "YYYY-MM-DD"
  }},
  "missing_parameters": ["list of critical parameters that are missing and needed"],
  "ambiguity": "Description of what is unclear, if anything",
  "clarification_question": "Question to ask user if route is clarification (in same language as user)",
  "clarification_options": ["Specific option 1", "Specific option 2", "Specific option 3"],
  "suggested_sql_approach": "Brief description of tables and joins needed"
}}
```

## ROUTING RULES

1. **Route to "database"** when:
   - Question is clearly about inspections, violations, locations, or inspectors
   - You have enough parameters OR can use reasonable defaults
   - Confidence is >= 0.7
   - Example: "How many inspections in 2024?" → database (year=2024 is clear)
   - Example: "Show violations" → database (no filters needed, show all)

2. **Route to "clarification"** when:
   - Question is about our data but is AMBIGUOUS
   - Critical parameters are missing that change the query significantly
   - Multiple very different interpretations are possible
   - Confidence is < 0.7
   - Example: "Show me the activity report" → clarification (which activity? what kind of report?)
   - Example: "Daily report" → clarification (daily inspections? violations? which date?)

3. **Route to "general"** when:
   - Question is completely outside our database scope
   - Question is about general knowledge (geography, history, science, etc.)
   - Question is a greeting or casual conversation
   - Example: "What is the capital of Spain?" → general
   - Example: "Hello, how are you?" → general

## CRITICAL RULES

1. **NEVER GUESS** - If the question is ambiguous, route to clarification
2. **Provide specific options** - Clarification options should be concrete choices the user can pick
3. **Match user's language** - If user asks in Arabic, clarification should be in Arabic
4. **Be helpful** - Clarification questions should guide the user toward a valid query
5. **Reasonable defaults** - If year is not specified, current year (2025) is acceptable
6. **List queries don't need filters** - "Show all locations" doesn't need clarification

RESPOND ONLY WITH THE JSON OBJECT, NO ADDITIONAL TEXT OR MARKDOWN FORMATTING.
"""

    def _get_sql_generation_prompt(self) -> str:
        """System prompt for generating SQL queries."""
        return f"""You are a SQL Server (T-SQL) expert for the AlUla Municipal Inspection System.

{self.schema_context}

## YOUR TASK

Generate a SQL Server query based on the user's question and the classification provided.

## SQL RULES

1. Use T-SQL syntax (SQL Server)
2. Use TOP N instead of LIMIT
3. Always filter by IsDeleted = 0 for Event and Locations tables
4. Use proper date formatting: YEAR(SubmitionDate), MONTH(SubmitionDate)
5. Use COALESCE for nullable fields
6. Include NameAr columns when selecting location/activity names
7. Use proper JOINs (LEFT JOIN for optional relationships)
8. Order results meaningfully (DESC for counts, ASC for names)
9. Use aliases for readability (e AS Event, l AS Locations)
10. Format numbers with appropriate aggregations

## COMMON QUERY PATTERNS

### Inspection Count by Year:
```sql
SELECT YEAR(SubmitionDate) as Year, COUNT(*) as InspectionCount
FROM Event
WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = @year
GROUP BY YEAR(SubmitionDate)
```

### Violations with Severity:
```sql
SELECT Severity, COUNT(*) as ViolationCount, SUM(ViolationValue) as TotalFines
FROM EventViolation
GROUP BY Severity
ORDER BY Severity
```

### Violations by Category (QuestionNameEn - this is how to group violations by "type"):
```sql
SELECT TOP 20
    COALESCE(QuestionNameEn, 'Unspecified') as ViolationType,
    COALESCE(QuestionNameAr, 'غير محدد') as ViolationTypeAr,
    COUNT(*) as ViolationCount, 
    SUM(ViolationValue) as TotalFines,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as Percentage
FROM EventViolation
GROUP BY QuestionNameEn, QuestionNameAr
ORDER BY ViolationCount DESC
```

### Top Inspectors:
```sql
SELECT TOP 10 ReporterID as InspectorID, COUNT(*) as InspectionCount
FROM Event
WHERE IsDeleted = 0
GROUP BY ReporterID
ORDER BY COUNT(*) DESC
```

### Locations List:
```sql
SELECT TOP 100 Id, Name, NameAr, Category
FROM Locations
WHERE Isdeleted = 0
ORDER BY Name
```

### Inspections by Business Type (Restaurants, Hotels, etc. - search by Name):
```sql
SELECT 
    l.Name as BusinessName, 
    l.NameAr as BusinessNameAr,
    COUNT(e.Id) as InspectionCount,
    AVG(e.Score) as AvgComplianceScore,
    SUM(CASE WHEN ev.Id IS NOT NULL THEN 1 ELSE 0 END) as ViolationCount
FROM Locations l
JOIN Event e ON e.Location = l.Id
LEFT JOIN EventViolation ev ON ev.EventId = e.Id
WHERE e.IsDeleted = 0 AND l.Isdeleted = 0
  AND (l.Name LIKE '%restaurant%' OR l.Name LIKE '%مطعم%' OR l.NameAr LIKE '%مطعم%')
GROUP BY l.Id, l.Name, l.NameAr
ORDER BY InspectionCount DESC
```
-- NOTE: For other business types, change the LIKE pattern to match the type name

### Daily Inspection Trend:
```sql
SELECT CAST(SubmitionDate AS DATE) as InspectionDate, COUNT(*) as DailyCount
FROM Event
WHERE IsDeleted = 0 AND SubmitionDate >= @date_from AND SubmitionDate <= @date_to
GROUP BY CAST(SubmitionDate AS DATE)
ORDER BY InspectionDate
```

## RESPONSE FORMAT

Return a JSON object:
```json
{{
  "sql": "Your complete SQL query here",
  "explanation": "Brief explanation of what this query returns",
  "expected_columns": ["column1", "column2"],
  "chart_type": "bar" | "line" | "pie" | "table" | "none",
  "chart_config": {{
    "xKey": "column name for x-axis",
    "yKey": "column name for y-axis",
    "title": "Chart title"
  }}
}}
```

RESPOND ONLY WITH THE JSON OBJECT, NO ADDITIONAL TEXT.
"""

    def _get_response_prompt(self) -> str:
        """System prompt for generating natural language responses."""
        return """You are a helpful assistant for the AlUla Municipal Inspection System.

Generate a clear, professional response based on the query results.

## RESPONSE RULES

1. Start with a brief summary of what was found
2. Use markdown tables for data with multiple rows (3+ rows)
3. Format numbers with commas (1,234 not 1234)
4. Highlight key insights or notable findings
5. Use appropriate emoji sparingly (📊 📈 ⚠️ ✅ 📍)
6. If no data found, explain what was searched and suggest alternatives
7. Keep response concise but informative
8. Match the user's language (Arabic response if question was in Arabic)

## TABLE FORMAT

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |

## EXAMPLE RESPONSES

Good: "📊 **2024 Inspection Summary**: Found 45,230 inspections with an average compliance score of 78.5%. Here's the monthly breakdown..."

Bad: "The query returned 45230 inspections." (Too terse, no formatting)

Generate a helpful, informative response.
"""

    def _call_claude(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> Dict[str, Any]:
        """Make a call to Claude API."""
        try:
            url = f"{self.endpoint}/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"❌ Claude API error: {response.status_code} - {response.text[:200]}")
                return {"error": f"API error: {response.status_code}"}
            
            result = response.json()
            text = result.get('content', [{}])[0].get('text', '')
            return {"success": True, "text": text}
            
        except requests.exceptions.Timeout:
            print("❌ Claude API timeout")
            return {"error": "Request timed out"}
        except Exception as e:
            print(f"❌ Claude API exception: {e}")
            return {"error": str(e)}

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from Claude's response, handling markdown code blocks."""
        try:
            # Clean up markdown code blocks if present
            cleaned = text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Raw text: {text[:500]}")
            return {"error": "Failed to parse response"}

    def process(self, message: str, session_id: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """
        Main entry point - process user message through intelligent routing.
        
        This is a synchronous version for compatibility with the existing API.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        print(f"\n{'='*60}")
        print(f"🧠 ORCHESTRATOR: Processing '{message}'")
        print(f"📍 Session: {session_id}")
        
        # Step 1: Check if this is a response to a pending clarification
        if session_id in self.pending_clarifications:
            return self._handle_clarification_response(session_id, message, language)
        
        # Step 2: Classify the question using Claude
        classification = self._classify_question(message)
        
        if "error" in classification:
            return self._error_response(
                "I'm having trouble understanding your question. Please try rephrasing it.",
                session_id
            )
        
        route = classification.get("route", "general")
        confidence = classification.get("confidence", 0.5)
        
        print(f"📋 Classification: route={route}, confidence={confidence}")
        print(f"📋 Intent: {classification.get('intent', 'unknown')}")
        
        # Step 3: Route based on classification
        if route == "clarification":
            return self._handle_clarification_needed(session_id, classification, message, language)
        
        elif route == "database":
            return self._handle_database_query(session_id, message, classification, language)
        
        else:  # route == "general"
            return self._handle_general_question(session_id, message, language)

    def _classify_question(self, message: str) -> Dict[str, Any]:
        """Use Claude to classify the user's question."""
        
        result = self._call_claude(
            system_prompt=self._get_classification_prompt(),
            user_message=f"Classify this user question:\n\n\"{message}\"",
            max_tokens=1500
        )
        
        if "error" in result:
            return result
        
        classification = self._parse_json_response(result.get("text", "{}"))
        
        if "error" in classification:
            # Fallback: assume general if parsing fails
            return {
                "route": "general",
                "confidence": 0.5,
                "intent": "Unknown - parse failed",
                "query_type": "general"
            }
        
        return classification

    def _handle_clarification_needed(
        self, 
        session_id: str, 
        classification: Dict[str, Any],
        original_message: str,
        language: str
    ) -> Dict[str, Any]:
        """Handle case where clarification is needed."""
        
        question = classification.get("clarification_question", "Could you please provide more details about what you're looking for?")
        options = classification.get("clarification_options", [])
        ambiguity = classification.get("ambiguity", "")
        
        # Store pending clarification state
        self.pending_clarifications[session_id] = {
            "original_message": original_message,
            "original_classification": classification,
            "timestamp": datetime.now().isoformat()
        }
        
        # Format response with numbered options
        if options:
            options_text = "\n".join([f"  {i+1}. {opt}" for i, opt in enumerate(options)])
            response_text = f"🤔 {question}\n\n{options_text}\n\n*Reply with a number (1-{len(options)}) or provide more details.*"
        else:
            response_text = f"🤔 {question}"
        
        print(f"❓ Requesting clarification: {question}")
        if ambiguity:
            print(f"   Ambiguity: {ambiguity}")
        
        return {
            "response": response_text,
            "response_ar": question if self._is_arabic(original_message) else "",
            "needs_clarification": True,
            "clarification_options": options,
            "session_id": session_id,
            "route": "clarification",
            "data": None,
            "chart_config": None,
            "type": "clarification_needed"
        }

    def _handle_clarification_response(
        self,
        session_id: str,
        message: str,
        language: str
    ) -> Dict[str, Any]:
        """Handle user's response to a clarification request."""
        
        pending = self.pending_clarifications.pop(session_id, None)
        if not pending:
            # No pending clarification found, treat as new question
            return self.process(message, session_id, language)
        
        original = pending.get("original_classification", {})
        original_message = pending.get("original_message", "")
        options = original.get("clarification_options", [])
        
        # Check if user selected a numbered option
        selected_option = None
        try:
            selection = int(message.strip()) - 1
            if 0 <= selection < len(options):
                selected_option = options[selection]
        except ValueError:
            pass
        
        if selected_option:
            # User picked an option - create enhanced query
            enhanced_message = f"{original_message} - specifically: {selected_option}"
            print(f"✅ Clarification resolved with option: {selected_option}")
        else:
            # User provided text - combine with original
            enhanced_message = f"{original_message}. Additional context: {message}"
            print(f"✅ Clarification resolved with text: {message}")
        
        # Re-process with enhanced context
        return self.process(enhanced_message, session_id, language)

    def _clean_data_for_json(self, data: List[Dict]) -> List[Dict]:
        """Clean data for JSON serialization by replacing NaN/None values."""
        import math
        cleaned = []
        for row in data:
            clean_row = {}
            for key, value in row.items():
                # Handle NaN, None, and infinity
                if value is None:
                    clean_row[key] = None
                elif isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    clean_row[key] = None
                else:
                    clean_row[key] = value
            cleaned.append(clean_row)
        return cleaned

    def _handle_database_query(
        self,
        session_id: str,
        message: str,
        classification: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Handle query that should be answered from database."""
        
        print(f"📊 Routing to DATABASE query")
        print(f"   Query type: {classification.get('query_type')}")
        print(f"   Parameters: {classification.get('parameters')}")
        
        # Step 1: Generate SQL using Claude
        sql_result = self._generate_sql(message, classification)
        
        if "error" in sql_result:
            return self._error_response(
                "I couldn't generate the right query for your question. Please try rephrasing it.",
                session_id
            )
        
        sql = sql_result.get("sql", "")
        print(f"📝 Generated SQL:\n{sql}")
        
        # Step 2: Execute query
        data = []
        try:
            from database import Database
            db = Database()
            df = db.execute_query(sql)
            
            if df is not None and not df.empty:
                # Convert to dict and clean NaN values for JSON serialization
                raw_data = df.to_dict(orient='records')
                data = self._clean_data_for_json(raw_data)
                print(f"✅ Query returned {len(data)} rows")
            else:
                print(f"⚠️ Query returned no data")
                
        except Exception as e:
            print(f"❌ SQL execution error: {e}")
            # Don't fail completely - try to give a helpful response
            return self._error_response(
                f"I encountered an issue running the query. Error: {str(e)[:100]}",
                session_id
            )
        
        # Step 3: Generate natural language response
        response = self._generate_response(message, data, sql_result, language)
        
        # Build chart config
        chart_config = None
        if data and sql_result.get("chart_type", "none") != "none":
            chart_config = {
                "type": sql_result.get("chart_type", "table"),
                "data": data,
                **sql_result.get("chart_config", {})
            }
        
        return {
            "response": response,
            "response_ar": "",  # TODO: Add Arabic response generation
            "data": data,
            "chart_config": chart_config,
            "session_id": session_id,
            "route": "database",
            "sql": sql,  # Include for debugging
            "needs_clarification": False,
            "intent": classification.get("intent"),
            "query_type": classification.get("query_type")
        }

    def _generate_sql(self, message: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to generate SQL query based on classification."""
        
        params = classification.get("parameters", {})
        query_type = classification.get("query_type", "")
        intent = classification.get("intent", "")
        sql_hint = classification.get("suggested_sql_approach", "")
        
        prompt = f"""Generate a SQL query for this request:

User question: "{message}"

Classification:
- Query type: {query_type}
- Intent: {intent}
- Suggested approach: {sql_hint}
- Parameters: {json.dumps(params, indent=2)}

Generate an appropriate SQL Server query to answer this question.
"""
        
        result = self._call_claude(
            system_prompt=self._get_sql_generation_prompt(),
            user_message=prompt,
            max_tokens=1500
        )
        
        if "error" in result:
            return result
        
        sql_response = self._parse_json_response(result.get("text", "{}"))
        
        if "error" in sql_response:
            # Try to extract SQL directly from response
            text = result.get("text", "")
            if "SELECT" in text.upper():
                # Find SQL in the response
                import re
                sql_match = re.search(r'SELECT.*?(?:;|$)', text, re.IGNORECASE | re.DOTALL)
                if sql_match:
                    return {
                        "sql": sql_match.group(0),
                        "chart_type": "table",
                        "explanation": "Extracted SQL"
                    }
            return {"error": "Failed to generate SQL"}
        
        return sql_response

    def _generate_response(
        self,
        question: str,
        data: List[Dict],
        sql_result: Dict[str, Any],
        language: str
    ) -> str:
        """Generate natural language response from query results."""
        
        if not data:
            return f"📭 No data found for your query. The search returned no results.\n\nTry adjusting your search criteria or ask about a different time period."
        
        # Prepare data preview (limit to avoid token overflow)
        data_preview = data[:20] if len(data) > 20 else data
        data_str = json.dumps(data_preview, indent=2, default=str)
        
        prompt = f"""Generate a response for this query result:

User asked: "{question}"

Query explanation: {sql_result.get('explanation', 'Data query')}

Results ({len(data)} total rows):
{data_str}

Generate a helpful, well-formatted response with the data.
"""
        
        result = self._call_claude(
            system_prompt=self._get_response_prompt(),
            user_message=prompt,
            max_tokens=1500
        )
        
        if "error" in result:
            # Fallback response
            return f"📊 Found {len(data)} results. Here's a summary of the data."
        
        return result.get("text", f"Found {len(data)} results.")

    def _handle_general_question(
        self,
        session_id: str,
        message: str,
        language: str
    ) -> Dict[str, Any]:
        """Handle general knowledge question outside database scope."""
        
        print(f"💬 Routing to GENERAL knowledge")
        
        system_prompt = """You are the AlUla Inspection Assistant, a helpful AI for the AlUla Municipal Inspection System in Saudi Arabia.

The user has asked a question that is outside the scope of the inspection database.

## YOUR TASK

1. If it's a greeting or casual chat, respond warmly and mention what you can help with
2. If it's a general knowledge question, provide a brief, helpful answer
3. Always end by mentioning that you specialize in inspection data

## WHAT YOU CAN HELP WITH (mention these):
- 📊 Inspection statistics and trends
- ⚠️ Violation analysis and patterns  
- 👥 Inspector performance metrics
- 📍 Location and business information
- 🔮 ML predictions and risk analysis

## RULES
- Be friendly and professional
- Keep response concise (2-3 paragraphs max)
- Do NOT make up any inspection data or statistics
- Match the user's language (Arabic if they wrote in Arabic)
"""
        
        result = self._call_claude(
            system_prompt=system_prompt,
            user_message=message,
            max_tokens=800
        )
        
        if "error" in result:
            response_text = "I'm here to help with AlUla inspection data! Feel free to ask about inspections, violations, compliance metrics, or location information."
        else:
            response_text = result.get("text", "")
        
        return {
            "response": response_text,
            "response_ar": "",
            "data": None,
            "chart_config": None,
            "session_id": session_id,
            "route": "general",
            "needs_clarification": False
        }

    def _error_response(self, message: str, session_id: str) -> Dict[str, Any]:
        """Generate an error response."""
        return {
            "response": f"⚠️ {message}",
            "response_ar": "",
            "data": None,
            "chart_config": None,
            "session_id": session_id,
            "route": "error",
            "needs_clarification": False
        }

    def _is_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters."""
        return any('\u0600' <= c <= '\u06FF' for c in text)


# Singleton instance
_orchestrator_instance = None

def get_orchestrator(db_connection=None) -> IntelligentOrchestrator:
    """Get or create the orchestrator singleton."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = IntelligentOrchestrator(db_connection)
    return _orchestrator_instance
