"""
Questions Library
==================
A comprehensive library of 1000+ predefined questions for the AlUla Inspection AI.

Categories:
- KPI Questions (100+): Compliance, Performance, Violations, Risk
- Analytics Questions (300+): Trends, Rankings, Distributions, Aggregates
- Prediction Questions (200+): Forecasting, Risk Scoring, Anomalies
- Comparison Questions (150+): Time Periods, Locations, Inspectors
- Temporal Questions (100+): Daily, Weekly, Monthly, Quarterly, Yearly
- Entity Questions (150+): Inspectors, Locations, Violations, Events
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class QuestionCategory(Enum):
    KPI = "kpi"
    ANALYTICS = "analytics"
    PREDICTION = "prediction"
    COMPARISON = "comparison"
    TEMPORAL = "temporal"
    ENTITY = "entity"


class OutputFormat(Enum):
    TABLE = "table"
    CHART = "chart"
    BOTH = "both"
    CALCULATION = "calculation"
    TEXT = "text"


class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    HEATMAP = "heatmap"
    SANKEY = "sankey"
    TREEMAP = "treemap"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    NONE = "none"


class Difficulty(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class QuestionTemplate:
    """A predefined question template with SQL, variations, and output configuration."""
    
    id: str                                    # Unique identifier (e.g., "KPI_COMP_001")
    category: QuestionCategory                 # Category of question
    subcategory: str                           # Subcategory (e.g., "violations", "compliance")
    intent: List[str]                          # Intent tags (e.g., ["COUNT", "TREND"])
    
    # Bilingual support
    question_en: str                           # Primary English question
    question_ar: str                           # Primary Arabic question
    variations_en: List[str] = field(default_factory=list)   # Alternative phrasings (EN)
    variations_ar: List[str] = field(default_factory=list)   # Alternative phrasings (AR)
    keywords_en: List[str] = field(default_factory=list)     # Semantic matching keywords
    keywords_ar: List[str] = field(default_factory=list)
    
    # Query configuration
    sql: str = ""                              # SQL query with placeholders
    parameters: Dict[str, type] = field(default_factory=dict)   # {year: int, location: str}
    default_values: Dict[str, Any] = field(default_factory=dict) # Default parameter values
    
    # Output configuration
    output_format: OutputFormat = OutputFormat.BOTH
    chart_type: ChartType = ChartType.BAR
    show_calculation_steps: bool = False       # Show step-by-step math
    
    # Metadata
    difficulty: Difficulty = Difficulty.BASIC
    usage_count: int = 0                       # Track popularity
    success_rate: float = 1.0                  # Track accuracy
    
    def get_all_variations(self, language: str = "en") -> List[str]:
        """Get all question variations including primary."""
        if language == "ar":
            return [self.question_ar] + self.variations_ar
        return [self.question_en] + self.variations_en
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "intent": self.intent,
            "question_en": self.question_en,
            "question_ar": self.question_ar,
            "variations_en": self.variations_en,
            "variations_ar": self.variations_ar,
            "keywords_en": self.keywords_en,
            "keywords_ar": self.keywords_ar,
            "sql": self.sql,
            "parameters": {k: v.__name__ for k, v in self.parameters.items()},
            "default_values": self.default_values,
            "output_format": self.output_format.value,
            "chart_type": self.chart_type.value,
            "show_calculation_steps": self.show_calculation_steps,
            "difficulty": self.difficulty.value,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }


class QuestionsRegistry:
    """Central registry for all question templates."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._templates: Dict[str, QuestionTemplate] = {}
            cls._instance._by_category: Dict[QuestionCategory, List[str]] = {
                cat: [] for cat in QuestionCategory
            }
            cls._instance._keywords_index: Dict[str, List[str]] = {}  # keyword -> template_ids
        return cls._instance
    
    def register(self, template: QuestionTemplate) -> None:
        """Register a question template."""
        self._templates[template.id] = template
        self._by_category[template.category].append(template.id)
        
        # Index keywords for fast lookup
        for keyword in template.keywords_en + template.keywords_ar:
            keyword_lower = keyword.lower()
            if keyword_lower not in self._keywords_index:
                self._keywords_index[keyword_lower] = []
            self._keywords_index[keyword_lower].append(template.id)
    
    def register_many(self, templates: List[QuestionTemplate]) -> None:
        """Register multiple templates."""
        for template in templates:
            self.register(template)
    
    def get(self, template_id: str) -> Optional[QuestionTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def get_by_category(self, category: QuestionCategory) -> List[QuestionTemplate]:
        """Get all templates in a category."""
        return [self._templates[tid] for tid in self._by_category[category]]
    
    def search_by_keyword(self, keyword: str) -> List[QuestionTemplate]:
        """Search templates by keyword."""
        keyword_lower = keyword.lower()
        template_ids = self._keywords_index.get(keyword_lower, [])
        return [self._templates[tid] for tid in template_ids]
    
    def find_best_match(self, query: str, threshold: float = 0.6) -> Optional[QuestionTemplate]:
        """Find the best matching template for a query."""
        query_lower = query.lower()
        best_match = None
        best_score = 0.0
        
        for template in self._templates.values():
            # Check all variations
            all_questions = template.get_all_variations("en") + template.get_all_variations("ar")
            
            for question in all_questions:
                score = self._calculate_similarity(query_lower, question.lower())
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = template
        
        return best_match
    
    def _calculate_similarity(self, query: str, template_question: str) -> float:
        """Calculate similarity score between query and template."""
        # Simple word overlap similarity (can be enhanced with embeddings)
        query_words = set(query.split())
        template_words = set(template_question.split())
        
        if not query_words or not template_words:
            return 0.0
        
        intersection = query_words & template_words
        union = query_words | template_words
        
        return len(intersection) / len(union)
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        return {
            "total_templates": len(self._templates),
            "by_category": {
                cat.value: len(ids) for cat, ids in self._by_category.items()
            },
            "total_keywords": len(self._keywords_index)
        }
    
    def all_templates(self) -> List[QuestionTemplate]:
        """Get all registered templates."""
        return list(self._templates.values())


# Global registry instance
registry = QuestionsRegistry()


# Import and register all question categories
def initialize_library():
    """Initialize the questions library by loading all categories."""
    from . import kpi_questions
    from . import analytics_questions
    from . import prediction_questions
    from . import comparison_questions
    from . import temporal_questions
    from . import entity_questions
    
    # Each module registers its templates on import
    print(f"Questions Library initialized: {registry.get_stats()}")


# Convenience exports
__all__ = [
    'QuestionTemplate',
    'QuestionCategory',
    'OutputFormat',
    'ChartType',
    'Difficulty',
    'QuestionsRegistry',
    'registry',
    'initialize_library'
]
