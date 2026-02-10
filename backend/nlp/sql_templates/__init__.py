"""
SQL Templates Package
=====================
Contains 80+ SQL templates organized by domain.
Includes auto-generated learned templates from the AI learning system.
"""

from .reports import TEMPLATES as REPORTS_TEMPLATES
from .violations import TEMPLATES as VIOLATIONS_TEMPLATES
from .inspectors import TEMPLATES as INSPECTORS_TEMPLATES
from .neighborhoods import TEMPLATES as NEIGHBORHOODS_TEMPLATES
from .forecasting import TEMPLATES as FORECASTING_TEMPLATES
from .complex import TEMPLATES as COMPLEX_TEMPLATES
from .analysis_4d import TEMPLATES as ANALYSIS_4D_TEMPLATES
from .learned import TEMPLATES as LEARNED_TEMPLATES

# Combine all templates (learned templates have priority)
ALL_TEMPLATES = {
    **REPORTS_TEMPLATES,
    **VIOLATIONS_TEMPLATES,
    **INSPECTORS_TEMPLATES,
    **NEIGHBORHOODS_TEMPLATES,
    **FORECASTING_TEMPLATES,
    **COMPLEX_TEMPLATES,
    **ANALYSIS_4D_TEMPLATES,
    **LEARNED_TEMPLATES  # Learned templates override if same ID
}

# Export by domain for easier access
__all__ = [
    'REPORTS_TEMPLATES',
    'VIOLATIONS_TEMPLATES', 
    'INSPECTORS_TEMPLATES',
    'NEIGHBORHOODS_TEMPLATES',
    'FORECASTING_TEMPLATES',
    'COMPLEX_TEMPLATES',
    'LEARNED_TEMPLATES',
    'ALL_TEMPLATES'
]
