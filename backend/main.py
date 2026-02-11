from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
from typing import List, Dict, Any, Optional
from database import Database

# Import the new NLP chat agent and feedback system
from nlp import InspectionChatAgent, InspectionChatAgentSync, get_feedback_system, get_orchestrator

load_dotenv()
app = FastAPI()

# CORS configuration - allow production domains
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


# New bilingual chat request model
class BilingualChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "en"  # "en" or "ar"


# Feedback validation request models
class FeedbackValidateRequest(BaseModel):
    message_id: str
    is_correct: bool  # True = correct, False = incorrect


class FeedbackClarifyRequest(BaseModel):
    message_id: str
    clarification: str
    expected_result: Optional[str] = None
    language: str = "en"  # Language of clarification


# ============================================================================
# INTELLIGENT AGENT - AlUla Inspection AI Assistant
# ============================================================================

class InspectionAgent:
    """Intelligent AI Agent for AlUla Inspection Analytics"""
    
    # Domain keywords - query MUST contain at least one to be considered relevant
    # NOTE: Do NOT include generic words like "what", "show", "how" - they appear in off-topic queries
    DOMAIN_KEYWORDS = {
        # Core inspection terms (English)
        'inspection', 'inspections', 'inspect', 'inspector', 'inspectors',
        'violation', 'violations', 'violate', 'violator',
        'compliance', 'compliant', 'non-compliant', 'noncompliant',
        'event', 'events',
        # Location/business terms
        'location', 'locations', 'business', 'businesses', 'site', 'sites', 'establishment',
        'activity', 'activities',
        # Metrics terms
        'score', 'scores', 'rating', 'ratings',
        'status', 'statuses',
        'category', 'categories',
        'kpi', 'kpis', 'metric', 'metrics', 'performance',
        'report', 'reports', 'reporting',
        # Domain-specific
        'alula', 'العلا',
        'municipal', 'municipality',
        'audit', 'audits',
        'fine', 'fines', 'penalty', 'penalties',
        'hygiene', 'sanitation',
        'restaurant', 'restaurants', 'shop', 'shops', 'store', 'stores',
        # Status terms
        'closed', 'pending', 'completed',
        # Analysis terms
        'trend', 'trends', 'forecast', 'prediction', 'predictions',
        'comparison', 'comparisons',
        'highest', 'lowest',
        'monthly', 'yearly', 'quarterly', 'daily', 'weekly',
        'statistics', 'stats', 'analytics',
        'risk', 'model', 'ml',
        # Arabic inspection-related terms
        'تفتيش', 'فحص', 'فحوصات', 'تفتيشات',
        'مفتش', 'مفتشين', 'المفتش', 'المفتشين',
        'مخالفة', 'مخالفات', 'المخالفة', 'المخالفات',
        'امتثال', 'الامتثال', 'ملتزم', 'غير ملتزم',
        'موقع', 'مواقع', 'الموقع', 'المواقع', 'مكان', 'أماكن',
        'نشاط', 'أنشطة', 'النشاط', 'الأنشطة',
        'حالة', 'الحالة', 'الوضع',
        'فئة', 'فئات', 'نوع', 'أنواع',
        'تقرير', 'تقارير', 'التقرير', 'التقارير',
        'أداء', 'الأداء', 'كفاءة',
        'درجة', 'درجات', 'تقييم',
        'غرامة', 'غرامات', 'عقوبة',
        'صحة', 'سلامة', 'نظافة',
        'مطعم', 'مطاعم', 'محل', 'محلات', 'متجر',
        'بلدية', 'البلدية',
        'مغلق', 'مفتوح', 'معلق', 'مكتمل',
        'اتجاه', 'توقع', 'تنبؤ',
        'مقارنة', 'قارن',
        'إجمالي', 'متوسط', 'عدد', 'كم',
        'شهري', 'سنوي', 'أسبوعي', 'يومي',
        'بيانات', 'إحصائيات', 'تحليل',
    }
    
    OFF_TOPIC_RESPONSE = """I'm the **AlUla Inspection Assistant** 🏛️, and I specialize in helping you analyze inspection data, compliance metrics, and municipal inspection activities for AlUla.

**I can help you with:**
• 📊 **Inspections** - Status, counts, trends, and results
• ⚠️ **Violations** - Types, severity, fines, and patterns
• ✅ **Compliance** - Scores, rankings, and performance
• 📍 **Locations** - Businesses, activities, and categories  
• 👥 **Inspectors** - Performance, workload, and statistics
• 🎯 **KPIs** - Key performance indicators and metrics
• 🔮 **Predictions** - ML forecasts and trend analysis

**Try asking:**
- "How many inspections were completed this month?"
- "Show me the top violations by category"
- "What's the compliance score trend?"
- "Which locations have the highest risk?"

Please ask me something about the AlUla inspection system!"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.db = Database()
        self.conversation_history: List[Dict[str, str]] = []
        
    def get_system_prompt(self) -> str:
        """Comprehensive system prompt for the AI agent"""
        return """You are the AlUla Inspection Intelligence Assistant, an advanced AI agent specialized in heritage site inspection analytics for AlUla, Saudi Arabia (a UNESCO World Heritage site).

## YOUR CAPABILITIES:
You have access to real-time inspection data and 9 ML prediction models:

### 10 KPIs You Can Report On:
1. Total Inspections - Count of all inspections conducted
2. Compliance Rate - Percentage of inspections without violations
3. Total Violations - Count of all violations detected
4. Inspector Count - Number of active inspectors
5. Average Inspection Time - Mean duration of inspections
6. Open Violations - Currently unresolved violations
7. High Severity Violations - Critical violations (severity >= 3)
8. Repeat Violations - Locations with recurring issues
9. Objection Rate - Percentage of violations with objections filed
10. Average Risk Score - Mean severity score across violations

### 9 ML Prediction Models:
1. ML_Predictions - Forecasting completion rates & compliance
2. ML_Location_Risk - Identifying high-risk heritage locations
3. ML_Anomalies - Detecting unusual inspection patterns
4. ML_Severity_Predictions - Predicting violation severity
5. ML_Scheduling_Recommendations - Optimal inspection scheduling
6. ML_Objection_Predictions - Objection outcome forecasts
7. ML_Location_Clusters - Location grouping analysis
8. ML_Recurrence_Predictions - Violation recurrence forecasts
9. ML_Inspector_Performance - Inspector tier classification

## YOUR BEHAVIOR:
1. Be conversational and helpful - Answer questions naturally
2. Use data when available - Reference specific numbers from the database
3. Explain insights clearly - Help users understand what the data means
4. Provide recommendations - Suggest actionable next steps
5. Handle general questions - You can answer questions about any topic, not just inspections
6. Be concise but complete - Don't over-explain, but cover the key points

## RESPONSE FORMAT:
- When presenting data with 3+ records, ALWAYS use Markdown tables
- Example table format:
| Inspector | Inspections | Score |
|-----------|-------------|-------|
| 23 | 11,271 | 46.97% |
| 2279 | 11,628 | 10.45% |

- Start with a brief summary (1-2 sentences)
- Present data in clean tables
- Format numbers with commas (1,234 not 1234)
- End with key insights or recommendations
- Keep responses focused and actionable

## CONTEXT:
You are helping inspection teams, managers, and analysts at AlUla understand their inspection data, identify risks, and improve compliance at heritage sites."""

    def get_database_context(self, message: str) -> str:
        """Fetch relevant database context based on the user's question"""
        msg_lower = message.lower()
        context_parts = []
        
        try:
            # Always try to get dashboard stats for context
            stats = self.db.get_dashboard_stats()
            if stats:
                context_parts.append(f"""CURRENT DASHBOARD STATS:
- Total Inspections: {stats.get('total_inspections', 'N/A')}
- Average Compliance Score: {stats.get('avg_compliance_score', 'N/A')}%
- High-Risk Locations: {stats.get('high_risk_locations', 'N/A')}
- Active ML Models: {stats.get('active_ml_models', 9)}""")
            
            # Get ML summary if asking about models/predictions
            if any(w in msg_lower for w in ['model', 'ml', 'prediction', 'forecast', 'ai', 'status', 'summary']):
                df = self.db.get_ml_summary()
                if not df.empty:
                    context_parts.append(f"ML MODEL STATUS:\n{df.to_string(index=False)}")
            
            # Get high-risk locations if relevant
            if any(w in msg_lower for w in ['risk', 'high-risk', 'dangerous', 'location', 'site']):
                df = self.db.get_high_risk_locations(5)
                if not df.empty:
                    context_parts.append(f"TOP HIGH-RISK LOCATIONS:\n{df.to_string(index=False)}")
            
            # Get inspector performance if relevant
            if any(w in msg_lower for w in ['inspector', 'performance', 'team', 'staff', 'employee']):
                df = self.db.get_inspector_performance()
                if not df.empty:
                    context_parts.append(f"INSPECTOR PERFORMANCE:\n{df.head(5).to_string(index=False)}")
            
            # Get anomalies if relevant
            if any(w in msg_lower for w in ['anomal', 'unusual', 'outlier', 'strange', 'weird']):
                df = self.db.get_anomalies(5)
                if not df.empty:
                    context_parts.append(f"DETECTED ANOMALIES:\n{df.to_string(index=False)}")
            
            # Get recurrence predictions if relevant
            if any(w in msg_lower for w in ['recur', 'repeat', 'again', 'pattern']):
                df = self.db.get_recurrence_predictions(5)
                if not df.empty:
                    context_parts.append(f"RECURRENCE PREDICTIONS:\n{df.to_string(index=False)}")
                    
        except Exception as e:
            print(f"⚠️ Database context error: {e}")
            # Don't add error to context, just continue without DB data
        
        return "\n\n".join(context_parts) if context_parts else ""

    def call_claude(self, user_message: str, context: str = "") -> str:
        """Call Claude API via Azure endpoint"""
        try:
            url = f"{self.endpoint}/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Build messages with conversation history
            messages = []
            for msg in self.conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append(msg)
            
            # Add current message with context
            if context:
                enhanced_message = f"{user_message}\n\n---\nRELEVANT DATA FROM DATABASE:\n{context}"
            else:
                enhanced_message = user_message
            
            messages.append({"role": "user", "content": enhanced_message})
            
            payload = {
                "model": "claude-sonnet-4-5",
                "max_tokens": 1500,
                "system": self.get_system_prompt(),
                "messages": messages
            }
            
            print(f"🔄 Calling Claude API...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return f"I'm having trouble connecting to the AI service (Status: {response.status_code}). Please check your API configuration."
            
            result = response.json()
            ai_text = result.get('content', [{}])[0].get('text', '')
            
            if not ai_text:
                return "I received an empty response. Please try again."
            
            return ai_text
            
        except requests.exceptions.Timeout:
            print("❌ API Timeout")
            return "The AI service is taking too long to respond. Please try again."
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {e}")
            return "Unable to connect to the AI service. Please check your network connection."
        except Exception as e:
            print(f"❌ Claude API Error: {e}")
            return f"An error occurred: {str(e)}"

    def detect_intent(self, message: str) -> str:
        """Detect the intent of the user's message"""
        msg_lower = message.lower()
        
        # Check for KPI dashboard/tiles request
        kpi_tile_keywords = ["show kpi", "show me kpi", "kpi dashboard", "all kpis", "list kpis", "kpi tiles", "show dashboard"]
        if any(kw in msg_lower for kw in kpi_tile_keywords):
            return "kpi_tiles"
        
        # Check for ML/prediction tiles request
        ml_tile_keywords = ["show prediction", "show ml", "ml models", "all models", "prediction tiles", "show models", "ai models"]
        if any(kw in msg_lower for kw in ml_tile_keywords):
            return "prediction_tiles"
        
        # Everything else goes to the AI for intelligent handling
        return "ai_chat"
    
    def _is_off_topic(self, message: str) -> bool:
        """Check if the query is completely off-topic (has NO relevance to inspections)"""
        msg_lower = message.lower().strip()
        
        # Check if ANY domain keyword is present
        for keyword in self.DOMAIN_KEYWORDS:
            if keyword.lower() in msg_lower:
                return False  # Found a domain keyword - NOT off-topic
        
        # No domain keywords found - this is off-topic
        print(f"⚠️ Off-topic query detected: '{message}'")
        return True

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Main entry point - process user message and return response"""
        print(f"\n{'='*60}")
        print(f"📨 USER: {user_message}")
        
        # FIRST: Check if query is completely off-topic
        if self._is_off_topic(user_message):
            return {
                "message": self.OFF_TOPIC_RESPONSE,
                "chart_data": None,
                "chart_type": None
            }
        
        intent = self.detect_intent(user_message)
        print(f"🎯 INTENT: {intent}")
        
        if intent == "kpi_tiles":
            return self.get_kpi_tiles_response()
        
        elif intent == "prediction_tiles":
            return self.get_prediction_tiles_response()
        
        else:
            # AI Chat - get context and call Claude
            context = self.get_database_context(user_message)
            print(f"📊 CONTEXT LENGTH: {len(context)} chars")
            
            ai_response = self.call_claude(user_message, context)
            print(f"🤖 AI RESPONSE: {ai_response[:100]}...")
            
            # Store in conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return {
                "message": ai_response,
                "chart_data": None,
                "chart_type": None
            }

    def get_kpi_tiles_response(self) -> Dict[str, Any]:
        """Return KPI tiles for the dashboard"""
        return {
            "type": "kpi_tiles",
            "tiles": [
                {"id": "kpi_01", "name": "Monthly Inspection Trends", "description": "Tracks inspection volume, types, and outcomes over time", "table": "Event"},
                {"id": "kpi_02", "name": "Compliance Rate Analysis", "description": "Measures compliance levels by month and establishment type", "table": "Event"},
                {"id": "kpi_03", "name": "Inspector Performance Metrics", "description": "Evaluates inspector workload, efficiency, and violation detection", "table": "Event"},
                {"id": "kpi_04", "name": "Violation Severity Distribution", "description": "Analyzes violations by severity level and financial impact", "table": "EventViolation"},
                {"id": "kpi_05", "name": "Geographic Distribution Analysis", "description": "Maps inspections and violations across regions", "table": "Event"},
                {"id": "kpi_06", "name": "Seasonal Patterns", "description": "Identifies seasonal trends in inspections and violations", "table": "Event"},
                {"id": "kpi_07", "name": "Objection & Resolution Rates", "description": "Tracks objection filing and resolution patterns", "table": "EventViolation"},
                {"id": "kpi_08", "name": "Top Violating Establishments", "description": "Identifies establishments with the most violations", "table": "Event"},
                {"id": "kpi_09", "name": "Violation Recurrence Analysis", "description": "Tracks repeat violations and improvement patterns", "table": "Event"},
                {"id": "kpi_10", "name": "Issue Category Analysis", "description": "Analyzes distribution of violations by question/category", "table": "EventViolation"}
            ]
        }

    def get_prediction_tiles_response(self) -> Dict[str, Any]:
        """Return ML prediction tiles for the dashboard"""
        return {
            "type": "prediction_tiles",
            "tiles": [
                {"id": "ml_pred_01", "name": "Inspection Volume Forecast", "description": "Future inspection trends and volume predictions", "table": "ML_Predictions", "model": "Prophet/ARIMA"},
                {"id": "ml_pred_02", "name": "Compliance Rate Forecast", "description": "Predicted compliance rates and risk levels", "table": "ML_Predictions", "model": "Time Series"},
                {"id": "ml_pred_03", "name": "Location Risk Assessment", "description": "Geographic risk zones and high-risk areas", "table": "ML_Location_Risk", "model": "Random Forest"},
                {"id": "ml_pred_04", "name": "Anomaly Detection", "description": "Unusual patterns and outlier inspections", "table": "ML_Anomalies", "model": "Isolation Forest"},
                {"id": "ml_pred_05", "name": "Severity Predictions", "description": "Predicted violation severity levels", "table": "ML_Severity_Predictions", "model": "XGBoost"},
                {"id": "ml_pred_06", "name": "Scheduling Recommendations", "description": "Optimal inspection timing and resource allocation", "table": "ML_Scheduling_Recommendations", "model": "Decision Tree"},
                {"id": "ml_pred_07", "name": "Objection Likelihood", "description": "Predicted objection rates and resolution outcomes", "table": "ML_Objection_Predictions", "model": "Logistic Regression"},
                {"id": "ml_pred_08", "name": "Location Clustering", "description": "Establishment groupings and violation patterns", "table": "ML_Location_Clusters", "model": "K-Means"},
                {"id": "ml_pred_09", "name": "Recurrence Risk Prediction", "description": "Repeat violation likelihood and improvement tracking", "table": "ML_Recurrence_Predictions", "model": "LSTM"},
                {"id": "ml_pred_10", "name": "Inspector Performance Forecast", "description": "Performance trends and efficiency predictions", "table": "ML_Inspector_Performance", "model": "Neural Network"}
            ]
        }

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# ============================================================================
# GLOBAL AGENT INSTANCES
# ============================================================================
agent = InspectionAgent()

# Initialize the new bilingual chat agent
try:
    bilingual_agent = InspectionChatAgent()
    print("✅ Bilingual NLP Chat Agent initialized")
except Exception as e:
    print(f"⚠️ Bilingual agent init error: {e}")
    bilingual_agent = None

# Initialize the Intelligent Orchestrator (Claude-first decision making)
try:
    intelligent_orchestrator = get_orchestrator()
    print("✅ Intelligent Orchestrator initialized")
except Exception as e:
    print(f"⚠️ Orchestrator init error: {e}")
    intelligent_orchestrator = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

# Store session IDs for clarification tracking
chat_sessions: Dict[str, str] = {}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - NOW POWERED BY INTELLIGENT ORCHESTRATOR
    
    The orchestrator uses Claude Sonnet 4.5 to:
    1. Analyze and classify every question
    2. Route to database queries when confident
    3. Ask clarifying questions when ambiguous
    4. Provide general answers when outside database scope
    """
    if intelligent_orchestrator:
        # Use session tracking for clarification follow-ups
        # For now, generate a new session per request (can be enhanced with cookies/headers)
        import uuid
        session_id = str(uuid.uuid4())
        
        result = intelligent_orchestrator.process(
            message=request.message,
            session_id=session_id,
            language="en"
        )
        
        # Format response for frontend compatibility
        return {
            "message": result.get("response", ""),
            "chart_data": result.get("data"),
            "chart_type": result.get("chart_config", {}).get("type") if result.get("chart_config") else None,
            "chart_config": result.get("chart_config"),
            "session_id": result.get("session_id"),
            "route": result.get("route"),
            "needs_clarification": result.get("needs_clarification", False),
            "clarification_options": result.get("clarification_options", [])
        }
    else:
        # Fallback to old agent if orchestrator failed to initialize
        return agent.process_message(request.message)


# New model for chat with session support
class ChatWithSessionRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "en"


@app.post("/api/chat/session")
async def chat_with_session(request: ChatWithSessionRequest):
    """
    Chat endpoint with session support for clarification follow-ups.
    
    Use this endpoint when you need to:
    1. Continue a conversation after a clarification request
    2. Track context across multiple messages
    
    The session_id from a previous response should be passed back
    to continue the conversation.
    """
    if intelligent_orchestrator:
        result = intelligent_orchestrator.process(
            message=request.message,
            session_id=request.session_id,
            language=request.language
        )
        
        return {
            "message": result.get("response", ""),
            "chart_data": result.get("data"),
            "chart_type": result.get("chart_config", {}).get("type") if result.get("chart_config") else None,
            "chart_config": result.get("chart_config"),
            "session_id": result.get("session_id"),
            "route": result.get("route"),
            "needs_clarification": result.get("needs_clarification", False),
            "clarification_options": result.get("clarification_options", []),
            "intent": result.get("intent"),
            "query_type": result.get("query_type")
        }
    else:
        return {
            "error": "Orchestrator not available",
            "message": "The intelligent chat system is not configured."
        }


@app.post("/api/v2/chat")
async def chat_v2(request: BilingualChatRequest):
    """
    Bilingual chat endpoint (Phase 2).
    Supports Arabic and English queries with inline charts.
    
    Request body:
    - message: User's question (Arabic or English)
    - session_id: Optional session ID for follow-up context
    - language: Response language preference ("en" or "ar")
    
    Response:
    - response: Natural language response (English)
    - response_ar: Arabic response
    - data: Query result data
    - chart_config: Chart configuration for rendering
    - session_id: Session ID for follow-ups
    """
    if not bilingual_agent:
        return {
            "error": "Bilingual chat agent not available",
            "response": "The bilingual chat system is not configured. Please check server logs.",
            "response_ar": "نظام الدردشة ثنائي اللغة غير متاح. يرجى التحقق من سجلات الخادم."
        }
    
    try:
        result = await bilingual_agent.process_query(
            query=request.message,
            session_id=request.session_id,
            language=request.language
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "response": f"An error occurred: {str(e)}",
            "response_ar": f"حدث خطأ: {str(e)}"
        }


@app.get("/api/v2/health")
async def health_v2():
    """Health check for bilingual chat agent"""
    if bilingual_agent:
        return bilingual_agent.health_check()
    return {
        "status": "not_initialized",
        "error": "Bilingual agent failed to initialize"
    }


@app.get("/api/v2/templates")
async def get_templates():
    """Get available SQL template count and info"""
    if bilingual_agent:
        return {
            "count": bilingual_agent.get_template_count(),
            "status": "ready"
        }
    return {"count": 0, "status": "not_initialized"}


@app.delete("/api/v2/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific chat session"""
    if bilingual_agent:
        bilingual_agent.clear_session(session_id)
        return {"success": True, "message": f"Session {session_id} cleared"}
    return {"success": False, "message": "Agent not available"}


# ============================================================================
# FEEDBACK VALIDATION ENDPOINTS
# ============================================================================

@app.post("/api/v2/feedback/validate")
async def validate_feedback(request: FeedbackValidateRequest):
    """
    Validate an AI response as correct or incorrect.
    
    Request body:
    - message_id: Unique ID of the message to validate
    - is_correct: True if response was correct, False if incorrect
    
    Response:
    - success: Whether validation was recorded
    - validation_status: 'correct' or 'incorrect'
    - needs_clarification: True if user should provide clarification
    - message_en/message_ar: Bilingual feedback message
    """
    try:
        feedback_system = get_feedback_system()
        
        if request.is_correct:
            # Import learning system for promotion
            from nlp.query_learning import QueryLearningSystem
            learning_system = QueryLearningSystem()
            result = feedback_system.validate_correct(
                message_id=request.message_id,
                learning_system=learning_system
            )
        else:
            result = feedback_system.validate_incorrect(
                message_id=request.message_id
            )
        
        return result
        
    except Exception as e:
        print(f"❌ Feedback validation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message_en": "Failed to record feedback",
            "message_ar": "فشل في تسجيل الملاحظات"
        }


@app.post("/api/v2/feedback/clarify")
async def submit_clarification(request: FeedbackClarifyRequest):
    """
    Submit clarification for an incorrect response.
    
    Request body:
    - message_id: Original message ID that was marked incorrect
    - clarification: User's clarification text
    - expected_result: What the user expected (optional)
    - language: Language of clarification ('en' or 'ar')
    
    Response:
    - success: Whether clarification was recorded
    - retry_context: Context for retrying the query
    - message_en/message_ar: Bilingual acknowledgment
    """
    try:
        feedback_system = get_feedback_system()
        
        result = feedback_system.submit_clarification(
            message_id=request.message_id,
            clarification=request.clarification,
            clarification_lang=request.language,
            expected_result=request.expected_result
        )
        
        # If we have retry context and the bilingual agent is available,
        # we can automatically retry with the clarified intent
        if result.get('success') and bilingual_agent and result.get('retry_context'):
            retry_ctx = result['retry_context']
            original_question = retry_ctx.get('original_question', '')
            clarification = retry_ctx.get('clarification', '')
            
            # Create enhanced query with clarification
            enhanced_query = f"{original_question} [User clarification: {clarification}]"
            
            try:
                # Process the clarified query
                retry_result = await bilingual_agent.process_query(
                    query=enhanced_query,
                    language=request.language
                )
                
                # Generate new message_id for retry
                new_message_id = feedback_system.generate_message_id()
                
                # Link the retry to original
                feedback_system.link_retry_response(
                    request.message_id,
                    new_message_id
                )
                
                # Add the new message_id to retry result
                retry_result['message_id'] = new_message_id
                retry_result['is_retry'] = True
                retry_result['original_message_id'] = request.message_id
                
                return {
                    **result,
                    'retry_response': retry_result
                }
            except Exception as retry_error:
                print(f"⚠️ Retry failed: {retry_error}")
                # Return just the clarification result without retry
                result['retry_failed'] = True
        
        return result
        
    except Exception as e:
        print(f"❌ Clarification error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message_en": "Failed to process clarification",
            "message_ar": "فشل في معالجة التوضيح"
        }


@app.get("/api/v2/feedback/status/{message_id}")
async def get_feedback_status(message_id: str):
    """
    Get the validation status for a specific message.
    
    Path params:
    - message_id: The message ID to check
    
    Response:
    - validation_status: Current status (pending, correct, incorrect, clarified)
    - validated_at: Timestamp of validation
    - promoted: Whether query was promoted to learning system
    """
    try:
        feedback_system = get_feedback_system()
        status = feedback_system.get_validation_status(message_id)
        
        if status:
            return {"success": True, **status}
        return {
            "success": False,
            "error": "Message not found"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/api/chat/clear")
async def clear_chat():
    """Clear conversation history"""
    agent.clear_history()
    return {"success": True, "message": "Conversation history cleared"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running", "agent": "AlUla Inspection AI", "version": "2.0"}

@app.get("/api/health")
async def health():
    """Detailed health check"""
    try:
        db = Database()
        stats = db.get_dashboard_stats()
        db_status = "connected" if stats.get('total_inspections', 0) > 0 else "no data"
    except:
        db_status = "disconnected"
    
    return {
        "status": "running",
        "database": db_status,
        "ai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "not configured"),
        "agent": "AlUla Inspection Intelligence Assistant"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
