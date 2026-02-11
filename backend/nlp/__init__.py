"""
NLP Query Engine for ELM AlUla Inspection AI
=============================================
Bilingual (Arabic/English) natural language to SQL query engine
powered by Claude Sonnet 4.5.

Modules:
- query_parser: Claude-powered intent and entity extraction
- sql_mapper: Maps parsed queries to SQL templates
- entity_dictionary: Bilingual entity cache (neighborhoods, activities, etc.)
- context_manager: In-memory conversation context per session
- response_generator: Formats responses with charts and bilingual text
- kpi_library: Core KPI definitions and calculations
- ml_predictions_library: ML prediction table queries
- chat_agent: Main orchestrator for the chatbot pipeline
- input_validator: Input validation and clarification system
"""

from .query_parser import QueryParser
from .sql_mapper import SQLMapper
from .entity_dictionary import EntityDictionary
from .context_manager import ContextManager
from .response_generator import ResponseGenerator
from .kpi_library import KPILibrary
from .ml_predictions_library import MLPredictionsLibrary
from .chat_agent import InspectionChatAgent, InspectionChatAgentSync
from .input_validator import InputValidator, ClarificationManager, get_validator, get_clarification_manager
from .feedback_system import FeedbackSystem, ValidatedQuery, ValidationStatus, get_feedback_system
from .orchestrator import IntelligentOrchestrator, get_orchestrator

__all__ = [
    'QueryParser',
    'SQLMapper', 
    'EntityDictionary',
    'ContextManager',
    'ResponseGenerator',
    'KPILibrary',
    'MLPredictionsLibrary',
    'InspectionChatAgent',
    'InspectionChatAgentSync',
    'InputValidator',
    'ClarificationManager',
    'get_validator',
    'get_clarification_manager',
    'FeedbackSystem',
    'ValidatedQuery',
    'ValidationStatus',
    'get_feedback_system',
    'IntelligentOrchestrator',
    'get_orchestrator'
]
