"""
Response Generator - Format responses with charts and bilingual text
=====================================================================
Generates natural language responses and chart configurations
based on query results and language preference.
"""

import os
import requests
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class ResponseGenerator:
    """
    Generates bilingual responses with chart configurations.
    Uses Claude for natural language response generation.
    """
    
    # AlUla brand colors
    COLORS = {
        'primary': '#104C64',      # Deep teal
        'secondary': '#C0754D',    # Warm terracotta  
        'accent': '#B6410F',       # Deep orange
        'success': '#10B981',      # Green
        'warning': '#F59E0B',      # Amber
        'danger': '#EF4444',       # Red
        'neutral': '#6B7280',      # Gray
    }
    
    CHART_COLORS = ['#104C64', '#C0754D', '#B6410F', '#10B981', '#F59E0B', '#6B7280']
    
    # Translation dictionary for common labels in data
    LABEL_TRANSLATIONS = {
        # Inspector labels
        'Inspector': 'المفتش',
        'inspector': 'المفتش',
        'Inspections': 'الفحوصات',
        'inspections': 'الفحوصات',
        'avg_score': 'متوسط الدرجة',
        'Avg Score': 'متوسط الدرجة',
        'total_inspections': 'إجمالي الفحوصات',
        'Total Inspections': 'إجمالي الفحوصات',
        
        # Violation labels
        'violations': 'المخالفات',
        'Violations': 'المخالفات',
        'violation_type': 'نوع المخالفة',
        'Violation Type': 'نوع المخالفة',
        'count': 'العدد',
        'Count': 'العدد',
        'total_violations': 'إجمالي المخالفات',
        'Total Violations': 'إجمالي المخالفات',
        
        # Status labels
        'Approved': 'موافق عليه',
        'Rejected': 'مرفوض',
        'Pending': 'قيد الانتظار',
        'Has Objection': 'يوجد اعتراض',
        'No Objection': 'لا يوجد اعتراض',
        'objection_status': 'حالة الاعتراض',
        'Objection Status': 'حالة الاعتراض',
        
        # Time labels  
        'month': 'الشهر',
        'Month': 'الشهر',
        'year': 'السنة',
        'Year': 'السنة',
        
        # Location labels
        'neighborhood': 'الحي',
        'Neighborhood': 'الحي',
        'location': 'الموقع',
        'Location': 'الموقع',
        'location_name': 'اسم الموقع',
        'Location Name': 'اسم الموقع',
        
        # Metric labels
        'compliance_rate': 'معدل الامتثال',
        'Compliance Rate': 'معدل الامتثال',
        'compliance': 'الامتثال',
        'Compliance': 'الامتثال',
        'score': 'الدرجة',
        'Score': 'الدرجة',
        'percentage': 'النسبة المئوية',
        'Percentage': 'النسبة المئوية',
        
        # Activity/Sector labels
        'activity_type': 'نوع النشاط',
        'Activity Type': 'نوع النشاط',
        'sector': 'القطاع',
        'Sector': 'القطاع',
        'event_type': 'نوع الحدث',
        'Event Type': 'نوع الحدث',
    }
    
    def __init__(
        self,
        azure_endpoint: str = None,
        azure_api_key: str = None
    ):
        self.endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = azure_api_key or os.getenv("AZURE_OPENAI_KEY")
        self.model = "claude-sonnet-4-5"
    
    # Contextual follow-up recommendations based on query type
    RECOMMENDATIONS = {
        'violations': [
            {'text_en': 'Show violations by severity', 'text_ar': 'عرض المخالفات حسب الخطورة', 'icon': 'alert'},
            {'text_en': 'Which locations have most violations?', 'text_ar': 'أي المواقع لديها أكثر المخالفات؟', 'icon': 'map'},
            {'text_en': 'Violation trends over time', 'text_ar': 'اتجاهات المخالفات بمرور الوقت', 'icon': 'trend'},
            {'text_en': 'Compare violations by month', 'text_ar': 'مقارنة المخالفات حسب الشهر', 'icon': 'calendar'},
        ],
        'inspections': [
            {'text_en': 'Who are the top inspectors?', 'text_ar': 'من هم أفضل المفتشين؟', 'icon': 'users'},
            {'text_en': 'Monthly inspection trends', 'text_ar': 'اتجاهات الفحوصات الشهرية', 'icon': 'trend'},
            {'text_en': 'Inspections by status', 'text_ar': 'الفحوصات حسب الحالة', 'icon': 'pie'},
            {'text_en': 'Show completed inspections', 'text_ar': 'عرض الفحوصات المكتملة', 'icon': 'check'},
        ],
        'compliance': [
            {'text_en': 'Locations with low compliance', 'text_ar': 'المواقع ذات الامتثال المنخفض', 'icon': 'alert'},
            {'text_en': 'Compliance trend this year', 'text_ar': 'اتجاه الامتثال هذا العام', 'icon': 'trend'},
            {'text_en': 'Compare compliance by neighborhood', 'text_ar': 'مقارنة الامتثال حسب الحي', 'icon': 'bar'},
            {'text_en': 'High-risk locations', 'text_ar': 'المواقع عالية المخاطر', 'icon': 'target'},
        ],
        'inspectors': [
            {'text_en': 'Inspector performance ranking', 'text_ar': 'ترتيب أداء المفتشين', 'icon': 'ranking'},
            {'text_en': 'Inspections by inspector', 'text_ar': 'الفحوصات حسب المفتش', 'icon': 'users'},
            {'text_en': 'Average inspections per inspector', 'text_ar': 'متوسط الفحوصات لكل مفتش', 'icon': 'bar'},
            {'text_en': 'Top 10 inspectors by violations found', 'text_ar': 'أفضل 10 مفتشين حسب المخالفات', 'icon': 'alert'},
        ],
        'locations': [
            {'text_en': 'Violations by location', 'text_ar': 'المخالفات حسب الموقع', 'icon': 'map'},
            {'text_en': 'Compare neighborhoods', 'text_ar': 'مقارنة الأحياء', 'icon': 'bar'},
            {'text_en': 'High-risk locations', 'text_ar': 'المواقع عالية المخاطر', 'icon': 'target'},
            {'text_en': 'Location compliance rates', 'text_ar': 'معدلات الامتثال للمواقع', 'icon': 'pie'},
        ],
        'default': [
            {'text_en': 'How many violations in 2025?', 'text_ar': 'كم عدد المخالفات في 2025؟', 'icon': 'alert'},
            {'text_en': 'Show monthly inspection trends', 'text_ar': 'عرض اتجاهات الفحوصات الشهرية', 'icon': 'trend'},
            {'text_en': 'Who are the top inspectors?', 'text_ar': 'من هم أفضل المفتشين؟', 'icon': 'users'},
            {'text_en': 'Compliance rate by location', 'text_ar': 'معدل الامتثال حسب الموقع', 'icon': 'map'},
        ]
    }

    def generate(self, parsed_query: Dict, data: List[Dict], 
                 language: str = 'en') -> Dict[str, Any]:
        """
        Generate complete response with message and chart.
        
        Args:
            parsed_query: Structured query from parser
            data: Query results from database
            language: Response language ('en' or 'ar')
            
        Returns:
            {message, message_ar, message_en, chart: {type, title, data, config}, recommendations}
        """
        # Generate chart configuration for both languages (with translated data)
        chart_en = self._build_chart_config(parsed_query, data, 'en')
        chart_ar = self._build_chart_config(parsed_query, data, 'ar')
        
        # Use the appropriate chart for the requested language
        # This ensures data labels are translated correctly
        chart = chart_ar if language == 'ar' else chart_en
        
        # Add both titles for frontend reference
        if chart and chart_en and chart_ar:
            chart['title_en'] = chart_en.get('title')
            chart['title_ar'] = chart_ar.get('title')
        
        # Generate natural language response in BOTH languages
        message_en = self._generate_message(parsed_query, data, 'en')
        message_ar = self._generate_message(parsed_query, data, 'ar')
        
        # Generate follow-up recommendations (includes both languages)
        recommendations = self._generate_recommendations(parsed_query, language)
        
        return {
            'message': message_ar if language == 'ar' else message_en,
            'message_en': message_en,
            'message_ar': message_ar,
            'language': language,
            'chart': chart,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, parsed_query: Dict, language: str) -> List[Dict]:
        """Generate contextual follow-up recommendations based on query type."""
        metric = parsed_query.get('metric', '').lower()
        intent = parsed_query.get('intent', '').lower()
        entities = parsed_query.get('entities', {})
        
        # Determine recommendation category
        if 'violation' in metric or 'violation' in intent:
            category = 'violations'
        elif 'inspector' in metric or entities.get('inspector'):
            category = 'inspectors'
        elif 'compliance' in metric or 'score' in metric:
            category = 'compliance'
        elif 'location' in metric or 'neighborhood' in metric or entities.get('neighborhood'):
            category = 'locations'
        elif 'inspection' in metric or 'event' in metric:
            category = 'inspections'
        else:
            category = 'default'
        
        # Get recommendations for this category
        recs = self.RECOMMENDATIONS.get(category, self.RECOMMENDATIONS['default'])
        
        # Format for frontend
        formatted = []
        for rec in recs:
            formatted.append({
                'text': rec['text_ar'] if language == 'ar' else rec['text_en'],
                'text_en': rec['text_en'],
                'text_ar': rec['text_ar'],
                'icon': rec['icon']
            })
        
        return formatted[:4]  # Return max 4 recommendations
    
    def _translate_data_value(self, value: Any, language: str) -> Any:
        """Translate data values to Arabic if needed."""
        if language != 'ar' or value is None:
            return value
        
        if isinstance(value, str):
            # Check if it's an "Inspector X" pattern
            inspector_match = re.match(r'^Inspector\s+(\d+)$', value, re.IGNORECASE)
            if inspector_match:
                return f"المفتش {inspector_match.group(1)}"
            
            # Translate known labels
            if value in self.LABEL_TRANSLATIONS:
                return self.LABEL_TRANSLATIONS[value]
            
            # Partial translations for compound labels
            result = value
            for eng, ar in self.LABEL_TRANSLATIONS.items():
                if eng in result:
                    result = result.replace(eng, ar)
            
            return result
        
        return value
    
    def _translate_data_for_chart(self, data: List[Dict], language: str) -> List[Dict]:
        """Translate all data values for chart display."""
        if not data:
            return data
        
        translated = []
        for row in data:
            translated_row = {}
            for key, value in row.items():
                # For Arabic, use _ar fields if available
                if language == 'ar':
                    # Check for Arabic alternative fields
                    ar_key = f"{key}_ar"
                    if ar_key in row and row[ar_key]:
                        # Use the Arabic value instead
                        translated_row[key] = row[ar_key]
                        continue
                    
                    # Skip the _ar keys themselves (already handled)
                    if key.endswith('_ar'):
                        continue
                    
                    # Translate the value using our translations
                    translated_row[key] = self._translate_data_value(value, language)
                else:
                    # For English, skip _ar fields
                    if key.endswith('_ar'):
                        continue
                    translated_row[key] = value
            translated.append(translated_row)
        
        return translated
    
    def _build_chart_config(self, parsed_query: Dict, data: List[Dict],
                           language: str) -> Optional[Dict]:
        """Build chart configuration based on query and data"""
        
        chart_type = parsed_query.get('chart_type', 'bar')
        
        if chart_type == 'none' or not data:
            return None
        
        if len(data) == 0:
            return None
            
        # Determine keys from data structure
        if not data:
            return None
        
        # Translate data values for Arabic language
        chart_data = self._translate_data_for_chart(data, language)
            
        sample = chart_data[0]
        keys = list(sample.keys())
        
        # Identify x and y keys based on data shape
        x_key = self._identify_x_key(keys, parsed_query)
        y_keys = self._identify_y_keys(keys, x_key, parsed_query)
        
        if not x_key or not y_keys:
            return None
        
        # Build title
        title = self._build_chart_title(parsed_query, language)
        
        # Build config based on chart type
        config = {
            'xKey': x_key,
            'yKeys': y_keys,
            'colors': self.CHART_COLORS[:len(y_keys)],
            'showLegend': len(y_keys) > 1,
            'stacked': chart_type == 'area',
            'language': language
        }
        
        # Add colorBy for map charts
        if chart_type == 'map':
            config['colorBy'] = parsed_query.get('colorBy', 'violations')
        
        return {
            'type': chart_type,
            'title': title,
            'data': chart_data,  # Use translated data
            'config': config
        }
    
    def _identify_x_key(self, keys: List[str], parsed_query: Dict) -> Optional[str]:
        """Identify the x-axis key from data keys"""
        # Priority order for x-axis
        x_candidates = [
            'month', 'month_name', 'monthname', 'year',
            'neighborhood', 'neighborhood_ar', 'neighborhood_en',
            'inspector', 'inspector_name', 'inspectorname',
            'activity', 'activity_type', 'category',
            'name', 'label', 'status'
        ]
        
        for candidate in x_candidates:
            for key in keys:
                if candidate in key.lower():
                    return key
        
        # Fallback to first non-numeric looking key
        for key in keys:
            if not any(n in key.lower() for n in ['count', 'total', 'sum', 'avg', 'rate', 'score']):
                return key
        
        return keys[0] if keys else None
    
    def _identify_y_keys(self, keys: List[str], x_key: str, 
                        parsed_query: Dict) -> List[str]:
        """Identify y-axis keys (numeric values)"""
        y_candidates = [
            'count', 'total', 'sum', 'avg', 'average', 'rate', 
            'score', 'value', 'amount', 'percentage', 'violations',
            'inspections', 'compliance'
        ]
        
        y_keys = []
        for key in keys:
            if key == x_key:
                continue
            for candidate in y_candidates:
                if candidate in key.lower():
                    y_keys.append(key)
                    break
        
        # If no matches, use remaining numeric-looking keys
        if not y_keys:
            y_keys = [k for k in keys if k != x_key][:2]
        
        return y_keys
    
    def _build_chart_title(self, parsed_query: Dict, language: str) -> str:
        """Build localized chart title"""
        metric = parsed_query.get('metric', 'data')
        intent = parsed_query.get('intent', 'COUNT')
        entities = parsed_query.get('entities', {})
        time_period = parsed_query.get('time_period', {})
        
        if language == 'ar':
            # Arabic title construction
            metric_ar = {
                'violations': 'المخالفات',
                'compliance': 'الامتثال',
                'inspections': 'التفتيش',
                'reports': 'البلاغات',
                'performance': 'الأداء'
            }.get(metric, metric)
            
            title = metric_ar
            
            if entities.get('neighborhood'):
                title += f" - {entities['neighborhood']}"
            
            if time_period.get('year'):
                title += f" {time_period['year']}"
                
        else:
            # English title construction
            metric_en = metric.replace('_', ' ').title()
            
            parts = [metric_en]
            
            if intent == 'TREND':
                parts.insert(0, 'Monthly')
            elif intent == 'RANKING':
                limit = parsed_query.get('limit', 10)
                parts.insert(0, f'Top {limit}')
            
            if entities.get('neighborhood'):
                parts.append(f"- {entities['neighborhood']}")
            
            if time_period.get('year'):
                parts.append(str(time_period['year']))
            
            title = ' '.join(parts)
        
        return title
    
    def _generate_message(self, parsed_query: Dict, data: List[Dict],
                         language: str) -> str:
        """Generate natural language response using Claude"""
        
        if not data:
            if language == 'ar':
                return "لم يتم العثور على بيانات تطابق استعلامك."
            return "No data found matching your query."
        
        try:
            url = f"{self.endpoint}/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Prepare data summary for Claude
            data_summary = self._summarize_data_for_response(data)
            
            system_prompt = self._get_response_system_prompt(language)
            
            user_content = f"""Generate a natural language response for this query result.

Query Intent: {parsed_query.get('intent')}
Metric: {parsed_query.get('metric')}
Entities: {parsed_query.get('entities')}
Time Period: {parsed_query.get('time_period')}

Data Summary:
{data_summary}

Total Records: {len(data)}

Respond in {'Arabic' if language == 'ar' else 'English'}.
Use Western numerals (1234, not ١٢٣٤).
Be concise but informative. Highlight key insights."""

            payload = {
                "model": self.model,
                "max_tokens": 500,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_content}]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('content', [{}])[0].get('text', self._fallback_message(data, language))
            else:
                return self._fallback_message(data, language)
                
        except Exception as e:
            print(f"⚠️ Response generation error: {e}")
            return self._fallback_message(data, language)
    
    def _get_response_system_prompt(self, language: str) -> str:
        """System prompt for response generation"""
        if language == 'ar':
            return """أنت مساعد تحليلات التفتيش البلدي لمنطقة العلا.
مهمتك هي تقديم ملخصات واضحة وموجزة لنتائج الاستعلامات.
استخدم الأرقام الغربية (1234).
أبرز الأرقام الرئيسية والاتجاهات.

## قواعد التنسيق:
- عند عرض بيانات متعددة (3 سجلات أو أكثر)، استخدم جداول Markdown
- مثال الجدول:
| المفتش | الفحوصات | الدرجة |
|--------|----------|--------|
| 23 | 11,271 | 46.97 |

- ابدأ بملخص موجز من سطر أو سطرين
- ثم اعرض البيانات في جدول
- اختم بالرؤى أو الملاحظات الرئيسية"""
        else:
            return """You are the AlUla Municipal Inspection Analytics Assistant.
Your task is to provide clear, concise summaries of query results.
Highlight key numbers and trends.

## FORMATTING RULES:
- When presenting multiple data points (3+ records), ALWAYS use Markdown tables
- Table example:
| Inspector | Inspections | Score |
|-----------|-------------|-------|
| 23 | 11,271 | 46.97 |
| 2279 | 11,628 | 10.45 |

- Start with a 1-2 sentence summary of key findings
- Present the data in a clean table format
- End with 1-2 key insights or observations
- Format numbers with commas (1,234 not 1234)
- Keep column headers short and clear
- Use appropriate column alignment"""
    
    def _summarize_data_for_response(self, data: List[Dict]) -> str:
        """Create a text summary of data for Claude"""
        if not data:
            return "No data"
        
        # Show first 5 and last 2 rows if more than 7
        if len(data) > 7:
            rows = data[:5] + [{'...': f'({len(data) - 7} more rows)'}] + data[-2:]
        else:
            rows = data
        
        lines = []
        for row in rows:
            line = ", ".join(f"{k}: {v}" for k, v in row.items())
            lines.append(line)
        
        return "\n".join(lines)
    
    def _fallback_message(self, data: List[Dict], language: str) -> str:
        """Fallback message when Claude response fails"""
        count = len(data)
        
        if language == 'ar':
            if count == 1:
                return f"تم العثور على سجل واحد."
            elif count == 2:
                return f"تم العثور على سجلين."
            elif count <= 10:
                return f"تم العثور على {count} سجلات."
            else:
                return f"تم العثور على {count} سجل."
        else:
            return f"Found {count:,} record{'s' if count != 1 else ''}."
    
    def format_number(self, value: float, language: str = 'en') -> str:
        """Format number with locale-appropriate formatting"""
        # Always use Western numerals per client request
        if isinstance(value, float):
            if value == int(value):
                return f"{int(value):,}"
            return f"{value:,.2f}"
        return f"{value:,}"
    
    def format_percentage(self, value: float, language: str = 'en') -> str:
        """Format percentage value"""
        formatted = f"{value:.1f}%"
        return formatted
