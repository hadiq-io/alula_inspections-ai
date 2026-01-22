# backend/ai_service.py
import requests
from typing import Dict, Any, List
import os
import json
from dotenv import load_dotenv
from database import Database
from ai_functions import AIFunctions

load_dotenv()

class AIService:
    def __init__(self):
        self.base_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_key = os.getenv('AZURE_OPENAI_KEY')
        self.deployment = os.getenv('AZURE_DEPLOYMENT_NAME')
        self.db = Database()
        self.functions = AIFunctions()
        self.conversation_history: List[Dict[str, str]] = []
        
    def get_system_prompt(self) -> str:
        return """You are the AlUla Inspection Intelligence Assistant.

CRITICAL RULES:
- NO emojis or special characters in responses
- Use plain text only
- When CONTEXT DATA is provided, answer directly with the numbers
- Be concise and professional
- Answer in plain English without formatting symbols

When context data appears in the user message, extract and use those numbers immediately."""

    def chat(self, user_message: str) -> Dict[str, Any]:
        if self._should_show_tiles(user_message):
            return self._generate_tiles_response(user_message)
        return self._chat_with_claude(user_message)
    
    def _should_show_tiles(self, message: str) -> bool:
        keywords = ["show me all", "list all", "what kpis", "available kpis", "show kpis", "kpi options", "ml models available", "show models"]
        return any(kw in message.lower() for kw in keywords)
    
    def _generate_tiles_response(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['kpi', 'metric', 'dashboard']):
            tiles = [
                {"id": "total_inspections", "name": "Total Inspections", "description": "Overall inspection count", "table": "Event"},
                {"id": "compliance_rate", "name": "Compliance Rate", "description": "Average compliance percentage", "table": "Event"},
                {"id": "avg_risk_score", "name": "Average Risk Score", "description": "Mean severity across violations", "table": "EventViolation"},
                {"id": "total_violations", "name": "Total Violations", "description": "All violations count", "table": "EventViolation"},
                {"id": "inspector_count", "name": "Total Inspectors", "description": "Active inspector count", "table": "Event"},
                {"id": "avg_inspection_time", "name": "Avg Inspection Time", "description": "Average completion time", "table": "Event"},
                {"id": "open_violations", "name": "Open Violations", "description": "Pending objections", "table": "EventViolation"},
                {"id": "high_severity_count", "name": "High Severity Violations", "description": "Critical violations count", "table": "EventViolation"},
                {"id": "repeat_violations", "name": "Repeat Violations", "description": "Recurring violation patterns", "table": "EventViolation"},
                {"id": "objection_rate", "name": "Objection Rate", "description": "Percentage with objections", "table": "EventViolation"}
            ]
            return {"type": "kpi_tiles", "tiles": tiles}
        
        elif any(w in msg_lower for w in ['ml', 'model', 'prediction', 'forecast']):
            tiles = [
                {"id": "predictions", "name": "Compliance Predictions", "description": "Future compliance forecasting"},
                {"id": "location_risk", "name": "Location Risk Analysis", "description": "High-risk location identification"},
                {"id": "anomalies", "name": "Anomaly Detection", "description": "Unusual pattern detection"},
                {"id": "severity", "name": "Severity Forecasting", "description": "Predict violation severity"},
                {"id": "scheduling", "name": "Smart Scheduling", "description": "Optimal inspection timing"},
                {"id": "objections", "name": "Objection Predictions", "description": "Forecast objection outcomes"},
                {"id": "clusters", "name": "Location Clustering", "description": "Group similar locations"},
                {"id": "recurrence", "name": "Recurrence Forecasting", "description": "Predict violation recurrence"},
                {"id": "inspector_performance", "name": "Inspector Performance", "description": "Tier classification"},
                {"id": "compliance_forecast", "name": "Compliance Forecast", "description": "Long-term compliance trends"}
            ]
            return {"type": "prediction_tiles", "tiles": tiles}
        
        return self._generate_tiles_response("show kpis")
    
    def _chat_with_claude(self, user_message: str) -> Dict[str, Any]:
        try:
            context_data = self._get_context_for_query(user_message)
            
            enhanced_message = user_message
            
            if context_data and 'data' in context_data and context_data['data']:
                data_text = json.dumps(context_data['data'], indent=2)
                enhanced_message = f"{user_message}\n\nCONTEXT DATA - USE THIS TO ANSWER:\n{data_text}"
            elif context_data and 'kpi' in context_data and 'value' in context_data:
                enhanced_message = f"{user_message}\n\nCONTEXT DATA - USE THIS TO ANSWER:\n{context_data['kpi']}: {context_data['value']}"
            
            url = f"{self.base_endpoint}/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.deployment,
                "max_tokens": 2000,
                "system": self.get_system_prompt(),
                "messages": [
                    {"role": "user", "content": enhanced_message}
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                return {
                    "message": f"API error: {response.text}",
                    "chart_data": None,
                    "chart_type": None,
                    "success": False
                }
            
            result = response.json()
            ai_message = result['content'][0]['text']
            
            return {
                "message": ai_message,
                "chart_data": context_data.get("data") if context_data else None,
                "chart_type": context_data.get("chart_type") if context_data else None,
                "chart_config": context_data.get("chart_config") if context_data else {},
                "success": True
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "message": f"Error: {str(e)}",
                "chart_data": None,
                "chart_type": None,
                "success": False
            }
    
    def _get_context_for_query(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        if any(kw in msg_lower for kw in ['total inspections', 'how many inspections', 'inspection count']):
            return self.functions.get_kpi_value("total_inspections")
        
        if any(kw in msg_lower for kw in ['compliance', 'compliance rate']):
            return self.functions.get_kpi_value("compliance_rate")
        
        if any(kw in msg_lower for kw in ['risk score', 'average risk', 'avg risk']):
            return self.functions.get_kpi_value("avg_risk_score")
        
        if any(kw in msg_lower for kw in ['total violations', 'violation count', 'how many violations']):
            return self.functions.get_kpi_value("total_violations")
        
        if any(kw in msg_lower for kw in ['inspector count', 'how many inspectors', 'total inspectors']):
            return self.functions.get_kpi_value("inspector_count")
        
        if any(kw in msg_lower for kw in ['inspection time', 'average time', 'duration']):
            return self.functions.get_kpi_value("avg_inspection_time")
        
        if any(kw in msg_lower for kw in ['open violations', 'pending violations', 'unresolved']):
            return self.functions.get_kpi_value("open_violations")
        
        if any(kw in msg_lower for kw in ['high severity', 'critical violations', 'severe violations']):
            return self.functions.get_kpi_value("high_severity_count")
        
        if any(kw in msg_lower for kw in ['repeat violations', 'recurring', 'recurrence', 'repeat offenders']):
            return self.functions.get_kpi_value("repeat_violations")
        
        if any(kw in msg_lower for kw in ['objection', 'objection rate', 'appeal rate']):
            return self.functions.get_kpi_value("objection_rate")
        
        if any(kw in msg_lower for kw in ['high risk', 'risky location', 'top risk', 'risk analysis']):
            return self.functions.get_location_risk(top_n=5)
        
        if any(kw in msg_lower for kw in ['inspector performance', 'inspector stats', 'top inspectors']):
            return self.functions.get_inspector_stats(top_n=5)
        
        return {}
    
    def clear_history(self):
        self.conversation_history = []
