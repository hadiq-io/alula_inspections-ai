"""
SQL Templates Package
=====================
Contains 80+ SQL templates organized by domain.
"""

from .reports import TEMPLATES as REPORTS_TEMPLATES
from .violations import TEMPLATES as VIOLATIONS_TEMPLATES
from .inspectors import TEMPLATES as INSPECTORS_TEMPLATES
from .neighborhoods import TEMPLATES as NEIGHBORHOODS_TEMPLATES
from .forecasting import TEMPLATES as FORECASTING_TEMPLATES
from .complex import TEMPLATES as COMPLEX_TEMPLATES
from .analysis_4d import TEMPLATES as ANALYSIS_4D_TEMPLATES

# Combine all templates
ALL_TEMPLATES = {
    **REPORTS_TEMPLATES,
    **VIOLATIONS_TEMPLATES,
    **INSPECTORS_TEMPLATES,
    **NEIGHBORHOODS_TEMPLATES,
    **FORECASTING_TEMPLATES,
    **COMPLEX_TEMPLATES,
    **ANALYSIS_4D_TEMPLATES
}

# Export by domain for easier access
__all__ = [
    'REPORTS_TEMPLATES',
    'VIOLATIONS_TEMPLATES', 
    'INSPECTORS_TEMPLATES',
    'NEIGHBORHOODS_TEMPLATES',
    'FORECASTING_TEMPLATES',
    'COMPLEX_TEMPLATES',
    'ALL_TEMPLATES'
]
