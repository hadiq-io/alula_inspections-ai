from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def detect_intent(message: str) -> str:
    msg_lower = message.lower()
    prediction_keywords = ["predict", "prediction", "forecast", "ml", "ai", "future", "risk", "anomaly", "recommend"]
    kpi_keywords = ["kpi", "kpis", "dashboard", "metrics", "analytics", "report", "historical", "compliance", "violations"]
    
    for keyword in prediction_keywords:
        if keyword in msg_lower:
            return "prediction"
    for keyword in kpi_keywords:
        if keyword in msg_lower:
            return "kpi"
    return "general"

def get_kpi_tiles_response():
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

def get_prediction_tiles_response():
    return {
        "type": "prediction_tiles",
        "tiles": [
            {"id": "ml_pred_01", "name": "Inspection Volume Forecast", "description": "Future inspection trends and volume predictions", "table": "ML_Predictions", "model": "KPI_01"},
            {"id": "ml_pred_02", "name": "Compliance Rate Forecast", "description": "Predicted compliance rates and risk levels", "table": "ML_Predictions", "model": "KPI_02"},
            {"id": "ml_pred_03", "name": "Location Risk Assessment", "description": "Geographic risk zones and high-risk areas", "table": "ML_Location_Risk", "model": "KPI_03"},
            {"id": "ml_pred_04", "name": "Anomaly Detection", "description": "Unusual patterns and outlier inspections", "table": "ML_Anomalies", "model": "KPI_04"},
            {"id": "ml_pred_05", "name": "Severity Predictions", "description": "Predicted violation severity levels", "table": "ML_Severity_Predictions", "model": "KPI_05"},
            {"id": "ml_pred_06", "name": "Scheduling Recommendations", "description": "Optimal inspection timing and resource allocation", "table": "ML_Scheduling_Recommendations", "model": "KPI_06"},
            {"id": "ml_pred_07", "name": "Objection Likelihood", "description": "Predicted objection rates and resolution outcomes", "table": "ML_Objection_Predictions", "model": "KPI_07"},
            {"id": "ml_pred_08", "name": "Location Clustering", "description": "Establishment groupings and violation patterns", "table": "ML_Location_Clusters", "model": "KPI_08"},
            {"id": "ml_pred_09", "name": "Recurrence Risk Prediction", "description": "Repeat violation likelihood and improvement tracking", "table": "ML_Recurrence_Predictions", "model": "KPI_09"},
            {"id": "ml_pred_10", "name": "Inspector Performance Forecast", "description": "Performance trends and efficiency predictions", "table": "ML_Inspector_Performance", "model": "KPI_10"}
        ]
    }

def call_claude_ai(user_message: str) -> str:
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        url = f"{endpoint}/v1/messages"
        headers = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
        payload = {
            "model": "claude-sonnet-4-5",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": user_message}],
            "system": "You are a helpful AlUla analytics assistant. Keep responses brief and conversational. NO MARKDOWN. NO asterisks. NO bold. NO formatting. Plain text only."
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        text = response.json()['content'][0]['text']
        text = text.replace('**', '').replace('*', '').replace('__', '').replace('_', '').replace('#', '')
        return text
    except:
        return "Hello! I'm your AlUla analytics assistant. Ask me about KPIs or predictions."

@app.post("/api/chat")
async def chat(request: ChatRequest):
    print(f"\n=== REQUEST: {request.message}")
    intent = detect_intent(request.message)
    print(f"=== INTENT: {intent}")
    
    if intent == "kpi":
        return get_kpi_tiles_response()
    elif intent == "prediction":
        return get_prediction_tiles_response()
    else:
        ai_response = call_claude_ai(request.message)
        return {"message": ai_response, "chart_data": None, "chart_type": None}

@app.delete("/api/chat/clear")
async def clear_chat():
    return {"success": True}

@app.get("/")
async def root():
    return {"status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
