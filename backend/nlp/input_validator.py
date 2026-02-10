"""
Input Validator & Clarification System
======================================
Validates user input against actual database data before processing.
Asks for clarification when the AI is not confident about the interpretation.

Key Features:
1. Entity validation against real database values
2. Confidence scoring for interpretations
3. Smart clarification questions
4. Concept disambiguation (inspectors vs inspections, events vs Event table)
"""

import os
import re
import json
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import pyodbc
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    confidence: float  # 0.0 to 1.0
    interpretation: Dict[str, Any]
    needs_clarification: bool
    clarification_question: Optional[str] = None
    clarification_options: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    matched_entities: Dict[str, Any] = field(default_factory=dict)
    unmatched_terms: List[str] = field(default_factory=list)


@dataclass
class DatabaseEntity:
    """Represents an entity found in the database"""
    table: str
    column: str
    value: Any
    arabic_value: Optional[str] = None
    match_score: float = 1.0


class InputValidator:
    """
    Validates and disambiguates user input against actual database data.
    
    Core Responsibilities:
    1. Load and cache actual database values (locations, activities, etc.)
    2. Match user terms to database entities with fuzzy matching
    3. Detect ambiguous or incorrect interpretations
    4. Generate helpful clarification questions
    5. Prevent common misinterpretations (inspectors vs inspections)
    """
    
    # Minimum confidence threshold before asking for clarification
    CONFIDENCE_THRESHOLD = 0.65
    
    # Common misinterpretation pairs - system will ask for clarification
    AMBIGUOUS_PAIRS = {
        ('inspector', 'inspection'): "Did you mean **inspectors** (people who conduct inspections) or **inspections** (the inspection events)?",
        ('event', 'events'): None,  # Disabled - events is unambiguous in this system
        ('location', 'neighborhood'): "Are you asking about a **specific business location** or a **general area/neighborhood**?",
        ('violation', 'compliance'): "Are you interested in **violations** (problems found) or **compliance rates** (success metrics)?",
    }
    
    # Concept mapping - what users say → what it means in the database
    CONCEPT_MAP = {
        # Inspector-related
        'inspector': {'table': 'Event', 'column': 'AssignTo', 'type': 'user_id'},
        'inspectors': {'table': 'Event', 'column': 'AssignTo', 'type': 'user_id'},
        'المفتش': {'table': 'Event', 'column': 'AssignTo', 'type': 'user_id'},
        'المفتشين': {'table': 'Event', 'column': 'AssignTo', 'type': 'user_id'},
        
        # Event/Inspection-related  
        'inspection': {'table': 'Event', 'column': None, 'type': 'record'},
        'inspections': {'table': 'Event', 'column': None, 'type': 'record'},
        'event': {'table': 'Event', 'column': None, 'type': 'record'},
        'events': {'table': 'Event', 'column': None, 'type': 'record'},
        'التفتيش': {'table': 'Event', 'column': None, 'type': 'record'},
        'الفحص': {'table': 'Event', 'column': None, 'type': 'record'},
        
        # Location-related
        'location': {'table': 'Locations', 'column': 'Name', 'type': 'entity'},
        'locations': {'table': 'Locations', 'column': 'Name', 'type': 'entity'},
        'place': {'table': 'Locations', 'column': 'Name', 'type': 'entity'},
        'business': {'table': 'Locations', 'column': 'Name', 'type': 'entity'},
        'الموقع': {'table': 'Locations', 'column': 'Name', 'type': 'entity'},
        'المواقع': {'table': 'Locations', 'column': 'Name', 'type': 'entity'},
        
        # Violation-related
        'violation': {'table': 'EventViolation', 'column': None, 'type': 'record'},
        'violations': {'table': 'EventViolation', 'column': None, 'type': 'record'},
        'المخالفة': {'table': 'EventViolation', 'column': None, 'type': 'record'},
        'المخالفات': {'table': 'EventViolation', 'column': None, 'type': 'record'},
        
        # Activity-related
        'activity': {'table': 'Activity', 'column': 'NAME', 'type': 'entity'},
        'activities': {'table': 'Activity', 'column': 'NAME', 'type': 'entity'},
        'النشاط': {'table': 'Activity', 'column': 'NAME', 'type': 'entity'},
        
        # Status-related
        'status': {'table': 'EventStatus', 'column': 'Status', 'type': 'entity'},
        'الحالة': {'table': 'EventStatus', 'column': 'Status', 'type': 'entity'},
    }
    
    # Terms that DO NOT exist in database - trigger immediate clarification
    UNKNOWN_CONCEPTS = {
        'health certificate': "I don't see a 'Health Certificates' table in the database. Are you looking for:\n1. **Inspection results** for health-related businesses?\n2. **Compliance status** of locations?\n3. **Specific violation types** related to health?",
        'certificate': "The database doesn't have a certificates table. Could you clarify:\n1. Are you looking for **compliance/inspection status**?\n2. **License information** for businesses?\n3. Something else?",
        'permit': "I don't see permits data directly. Are you looking for:\n1. **Location/business information**?\n2. **Inspection history**?\n3. **Compliance records**?",
        'neighborhood': "The database stores individual **business locations**, not neighborhoods. Would you like to:\n1. See locations by **category**?\n2. See locations in a specific **area** (lat/long)?\n3. List all **locations** with their details?",
        'old town': "I don't have 'Old Town' as a specific filter. Would you like to:\n1. Search for locations with 'Old' in the name?\n2. See all **location categories**?\n3. View the **location list**?",
    }
    
    def __init__(self):
        """Initialize the validator with database connection"""
        self.db_server = os.getenv("DB_SERVER", "20.3.236.169")
        self.db_port = os.getenv("DB_PORT", "1433")
        self.db_name = os.getenv("DB_NAME", "CHECK_ELM_AlUlaRC_DW")
        self.db_user = os.getenv("DB_USERNAME", "sa")
        self.db_password = os.getenv("DB_PASSWORD", "StrongPass123!")
        
        # Cache for database values
        self._cache: Dict[str, Set[str]] = {}
        self._cache_loaded = False
        
    def _get_connection(self):
        """Get database connection"""
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.db_server},{self.db_port};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_user};"
            f"PWD={self.db_password};"
            f"TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str, timeout=30)
    
    def _load_cache(self) -> None:
        """Load database values into cache for fast validation"""
        if self._cache_loaded:
            return
            
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Load location names (both English and Arabic)
            cursor.execute("SELECT DISTINCT Name, NameAr FROM Locations WHERE Isdeleted = 0")
            locations = set()
            for row in cursor.fetchall():
                if row[0]:
                    locations.add(row[0].lower().strip())
                if row[1]:
                    locations.add(row[1].strip())
            self._cache['locations'] = locations
            
            # Load activity names
            cursor.execute("SELECT DISTINCT NAME, NameAr FROM Activity WHERE IsDeleted = 0 AND NAME IS NOT NULL")
            activities = set()
            for row in cursor.fetchall():
                if row[0]:
                    activities.add(row[0].lower().strip())
                if row[1]:
                    activities.add(row[1].strip())
            self._cache['activities'] = activities
            
            # Load distinct inspector IDs (AssignTo)
            cursor.execute("SELECT DISTINCT AssignTo FROM Event WHERE AssignTo IS NOT NULL")
            inspectors = set()
            for row in cursor.fetchall():
                if row[0]:
                    inspectors.add(str(row[0]))
            self._cache['inspectors'] = inspectors
            
            # Load event statuses
            cursor.execute("SELECT DISTINCT Status FROM Event WHERE Status IS NOT NULL")
            statuses = set()
            for row in cursor.fetchall():
                if row[0] is not None:
                    statuses.add(str(row[0]))
            self._cache['statuses'] = statuses
            
            # Load location categories
            cursor.execute("SELECT DISTINCT Category FROM Locations WHERE Category IS NOT NULL")
            categories = set()
            for row in cursor.fetchall():
                if row[0]:
                    categories.add(str(row[0]))
            self._cache['categories'] = categories
            
            # Load table names for reference
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = set()
            for row in cursor.fetchall():
                tables.add(row[0].lower())
            self._cache['tables'] = tables
            
            conn.close()
            self._cache_loaded = True
            print(f"✅ InputValidator cache loaded: {len(locations)} locations, {len(activities)} activities, {len(inspectors)} inspectors")
            
        except Exception as e:
            print(f"❌ Error loading validator cache: {e}")
            self._cache_loaded = False
    
    def validate(self, user_input: str, parsed_intent: Dict[str, Any] = None) -> ValidationResult:
        """
        Validate user input and determine if clarification is needed.
        
        Args:
            user_input: The raw user message
            parsed_intent: Optional already-parsed intent from query_parser
            
        Returns:
            ValidationResult with confidence score and clarification if needed
        """
        self._load_cache()
        
        input_lower = user_input.lower().strip()
        warnings = []
        unmatched_terms = []
        matched_entities = {}
        confidence = 1.0
        
        # Step 1: Check for completely unknown concepts
        for unknown_term, clarification in self.UNKNOWN_CONCEPTS.items():
            if unknown_term in input_lower:
                return ValidationResult(
                    is_valid=False,
                    confidence=0.3,
                    interpretation={'original': user_input, 'detected_unknown': unknown_term},
                    needs_clarification=True,
                    clarification_question=clarification,
                    clarification_options=self._get_available_options(unknown_term),
                    unmatched_terms=[unknown_term]
                )
        
        # Step 2: Check for ambiguous pairs
        for (term1, term2), clarification in self.AMBIGUOUS_PAIRS.items():
            # Skip if clarification is None (disabled)
            if clarification is None:
                continue
                
            # Check if BOTH terms could apply (user said something ambiguous)
            term1_match = self._fuzzy_match(input_lower, term1)
            term2_match = self._fuzzy_match(input_lower, term2)
            
            if term1_match > 0.7 and term2_match > 0.7:
                # Ambiguous - could be either
                return ValidationResult(
                    is_valid=False,
                    confidence=0.5,
                    interpretation={'original': user_input, 'ambiguous_terms': [term1, term2]},
                    needs_clarification=True,
                    clarification_question=clarification,
                    clarification_options=[term1, term2]
                )
        
        # Step 3: Extract and validate entities from input
        extracted_concepts = self._extract_concepts(input_lower)
        
        for concept, info in extracted_concepts.items():
            if info['type'] == 'entity':
                # Validate against database cache
                cache_key = self._get_cache_key(info['table'])
                if cache_key and cache_key in self._cache:
                    # Look for matching values
                    found = False
                    for cached_val in self._cache[cache_key]:
                        if self._fuzzy_match(input_lower, cached_val.lower()) > 0.7:
                            matched_entities[concept] = cached_val
                            found = True
                            break
                    
                    if not found:
                        unmatched_terms.append(concept)
                        confidence -= 0.15
        
        # Step 4: Validate parsed intent if provided
        if parsed_intent:
            confidence = self._validate_parsed_intent(parsed_intent, confidence)
        
        # Step 5: Determine if clarification is needed based on confidence
        needs_clarification = confidence < self.CONFIDENCE_THRESHOLD
        clarification_question = None
        clarification_options = []
        
        if needs_clarification:
            clarification_question, clarification_options = self._generate_clarification(
                user_input, unmatched_terms, extracted_concepts
            )
        
        return ValidationResult(
            is_valid=confidence >= self.CONFIDENCE_THRESHOLD,
            confidence=confidence,
            interpretation={
                'original': user_input,
                'extracted_concepts': extracted_concepts,
                'parsed_intent': parsed_intent
            },
            needs_clarification=needs_clarification,
            clarification_question=clarification_question,
            clarification_options=clarification_options,
            warnings=warnings,
            matched_entities=matched_entities,
            unmatched_terms=unmatched_terms
        )
    
    def _extract_concepts(self, input_text: str) -> Dict[str, Dict[str, Any]]:
        """Extract database concepts from user input"""
        concepts = {}
        
        for term, mapping in self.CONCEPT_MAP.items():
            if term.lower() in input_text.lower():
                concepts[term] = mapping
        
        return concepts
    
    def _get_cache_key(self, table_name: str) -> Optional[str]:
        """Map table name to cache key"""
        mapping = {
            'Locations': 'locations',
            'Activity': 'activities',
            'Event': 'inspectors',  # AssignTo field
            'EventStatus': 'statuses'
        }
        return mapping.get(table_name)
    
    def _fuzzy_match(self, text: str, term: str) -> float:
        """Simple fuzzy matching score between text and term"""
        if term.lower() in text.lower():
            return 1.0
        
        # Check for partial match
        term_words = term.lower().split()
        text_words = text.lower().split()
        
        matches = sum(1 for tw in term_words if any(tw in w or w in tw for w in text_words))
        if matches > 0:
            return matches / len(term_words)
        
        return 0.0
    
    def _validate_parsed_intent(self, parsed: Dict[str, Any], current_confidence: float) -> float:
        """Validate parsed intent against database reality"""
        confidence = current_confidence
        
        # Check if the metric/table exists
        metric = parsed.get('metric', '')
        
        # Validate entities
        entities = parsed.get('entities', {})
        
        if entities.get('neighborhood'):
            # We don't have neighborhoods - it's locations
            if 'locations' in self._cache:
                if not any(entities['neighborhood'].lower() in loc.lower() 
                          for loc in self._cache['locations']):
                    confidence -= 0.3
        
        if entities.get('inspector'):
            # Check if inspector exists
            if 'inspectors' in self._cache:
                if str(entities['inspector']) not in self._cache['inspectors']:
                    confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_clarification(
        self, 
        user_input: str, 
        unmatched_terms: List[str],
        concepts: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Generate a helpful clarification question"""
        
        input_lower = user_input.lower()
        
        if unmatched_terms:
            # User mentioned something we can't find
            question = f"I want to make sure I understand your request correctly. "
            
            if any('inspector' in term.lower() for term in unmatched_terms):
                question += "When you mention inspectors, are you looking for:\n"
                options = [
                    "Top inspectors by completed inspections",
                    "Inspector performance rankings",
                    "All active inspector IDs",
                    "Something else - please describe"
                ]
            elif 'event' in input_lower or 'inspection' in input_lower:
                question += "For events/inspections, would you like:\n"
                options = [
                    "Total inspection count",
                    "Recent inspection activity",
                    "Inspections by status",
                    "Inspection trends over time"
                ]
            elif 'violation' in input_lower:
                question += "For violations data, what would you like to see:\n"
                options = [
                    "Total violation count",
                    "Violations by severity",
                    "Open/unresolved violations",
                    "Violation trends"
                ]
            elif 'location' in input_lower or 'business' in input_lower:
                question += "For location data, what are you interested in:\n"
                options = [
                    "List of all business locations",
                    "Locations by category",
                    "Location inspection history",
                    "High-risk locations"
                ]
            else:
                question += "Could you please clarify what data you're looking for?\n"
                options = [
                    "📍 Locations - Business locations and their details",
                    "📋 Events/Inspections - Inspection records and results",
                    "⚠️ Violations - Violation records and statistics",
                    "📊 ML Predictions - AI-powered insights and forecasts"
                ]
            
            return question, options
        
        # Check what concepts were extracted and provide relevant options
        if 'inspector' in concepts or 'inspectors' in concepts:
            return (
                "What would you like to know about inspectors?\n",
                [
                    "Top 10 inspectors by inspections completed",
                    "Inspector performance summary",
                    "List all active inspectors"
                ]
            )
        
        if 'event' in concepts or 'events' in concepts or 'inspection' in concepts:
            return (
                "What would you like to know about inspections/events?\n",
                [
                    "Total number of inspections",
                    "Recent inspection activity",
                    "Inspection status breakdown"
                ]
            )
        
        # General clarification
        return (
            "I want to make sure I give you the right information. What type of data are you looking for?\n",
            [
                "Events/Inspections - Inspection activity data",
                "Violations - Violation records",
                "Locations - Business location information",
                "ML Analytics - Predictions and insights"
            ]
        )
    
    def _get_available_options(self, unknown_term: str) -> List[str]:
        """Get available database options related to an unknown term"""
        options = []
        
        if 'health' in unknown_term or 'certificate' in unknown_term:
            options = [
                "View inspection results by location",
                "See compliance statistics",
                "Check violation records",
                "View ML predictions"
            ]
        elif 'neighborhood' in unknown_term or 'area' in unknown_term:
            options = [
                "List all locations",
                "View locations by category",
                "See location statistics"
            ]
        else:
            options = [
                "Events/Inspections data",
                "Violations data",
                "Location data",
                "ML Analytics"
            ]
        
        return options
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Return a summary of what's available in the database"""
        self._load_cache()
        
        return {
            'available_tables': [
                'Event (inspections/events)',
                'Locations (business locations)',
                'EventViolation (violations)',
                'Activity (activity types)',
                'ML_Predictions (9 ML models)'
            ],
            'counts': {
                'locations': len(self._cache.get('locations', set())),
                'activities': len(self._cache.get('activities', set())),
                'inspectors': len(self._cache.get('inspectors', set())),
                'statuses': len(self._cache.get('statuses', set()))
            },
            'sample_data': {
                'locations': list(self._cache.get('locations', set()))[:5],
                'inspectors': list(self._cache.get('inspectors', set()))[:5]
            }
        }
    
    def suggest_query(self, user_input: str) -> List[str]:
        """Suggest valid queries based on user input"""
        input_lower = user_input.lower()
        suggestions = []
        
        if 'inspector' in input_lower:
            suggestions = [
                "Show top 10 inspectors by event count",
                "Which inspector completed the most inspections?",
                "Inspector performance summary"
            ]
        elif 'event' in input_lower or 'inspection' in input_lower:
            suggestions = [
                "How many events were completed this month?",
                "Show recent inspection activity",
                "Event status breakdown"
            ]
        elif 'violation' in input_lower:
            suggestions = [
                "Total violations this year",
                "Violations by severity",
                "Open violations count"
            ]
        elif 'location' in input_lower:
            suggestions = [
                "List all active locations",
                "Locations by category",
                "Location inspection history"
            ]
        else:
            suggestions = [
                "Show me the KPI dashboard",
                "What are the ML predictions?",
                "Give me an overview of inspections"
            ]
        
        return suggestions


class ClarificationManager:
    """
    Manages the clarification conversation flow.
    Handles multi-turn clarification dialogues.
    """
    
    def __init__(self):
        self.pending_clarifications: Dict[str, ValidationResult] = {}
    
    def request_clarification(
        self, 
        session_id: str, 
        validation_result: ValidationResult
    ) -> Dict[str, Any]:
        """
        Create a clarification request response.
        
        Args:
            session_id: The user's session ID
            validation_result: The validation result that triggered clarification
            
        Returns:
            A response dict with clarification question and options
        """
        # Store pending clarification for this session
        self.pending_clarifications[session_id] = validation_result
        
        response = {
            'type': 'clarification_needed',
            'message': validation_result.clarification_question,
            'options': validation_result.clarification_options,
            'confidence': validation_result.confidence,
            'original_input': validation_result.interpretation.get('original', ''),
            'suggestions': [],
        }
        
        # Add helpful suggestions
        if validation_result.unmatched_terms:
            response['unmatched'] = validation_result.unmatched_terms
            response['hint'] = "Some terms in your question don't match our database. Please choose from the options above."
        
        return response
    
    def handle_clarification_response(
        self, 
        session_id: str, 
        user_response: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Handle user's response to clarification.
        
        Args:
            session_id: The user's session ID
            user_response: The user's clarification response
            
        Returns:
            Tuple of (is_resolved, clarified_intent)
        """
        if session_id not in self.pending_clarifications:
            return False, None
        
        pending = self.pending_clarifications[session_id]
        
        # Check if user selected one of the options
        user_lower = user_response.lower().strip()
        
        for option in pending.clarification_options:
            if user_lower in option.lower() or option.lower() in user_lower:
                # User selected this option
                del self.pending_clarifications[session_id]
                return True, option
        
        # Check for numeric selection (1, 2, 3, etc.)
        if user_response.strip().isdigit():
            idx = int(user_response.strip()) - 1
            if 0 <= idx < len(pending.clarification_options):
                selected = pending.clarification_options[idx]
                del self.pending_clarifications[session_id]
                return True, selected
        
        return False, None
    
    def has_pending_clarification(self, session_id: str) -> bool:
        """Check if session has a pending clarification"""
        return session_id in self.pending_clarifications
    
    def clear_pending(self, session_id: str) -> None:
        """Clear pending clarification for session"""
        if session_id in self.pending_clarifications:
            del self.pending_clarifications[session_id]


# Singleton instances
_validator_instance: Optional[InputValidator] = None
_clarification_manager: Optional[ClarificationManager] = None


def get_validator() -> InputValidator:
    """Get singleton validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = InputValidator()
    return _validator_instance


def get_clarification_manager() -> ClarificationManager:
    """Get singleton clarification manager instance"""
    global _clarification_manager
    if _clarification_manager is None:
        _clarification_manager = ClarificationManager()
    return _clarification_manager
