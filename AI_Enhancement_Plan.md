# Intelligent AI Chatbot Enhancement Plan
## AlUla Inspection AI - Database Analytics Assistant

**Date:** February 11, 2026  
**Project:** alula-inspection-ai  
**Objective:** Build a smarter, self-learning AI assistant with 1000+ predefined questions, better output formatting, user feedback (👍/👎), correction learning, and improved conversational interaction.

---

## Executive Summary

Transform the current AI chatbot into an intelligent, self-improving analytics assistant that can:
- Answer 1000+ predefined questions about KPIs, analytics, and predictions
- Learn from user corrections when outputs are wrong
- Display data in proper formats (tables, charts, diagrams, calculations)
- Provide contextual suggestions for deeper analysis
- Understand natural follow-up questions

---

## Current Architecture

### Backend Components
| Component | File | Purpose |
|-----------|------|---------|
| Chat Agent V2 | `backend/nlp/chat_agent_v2.py` | Hybrid 5-tier query routing with self-learning |
| KPI Library | `backend/nlp/kpi_library.py` | 10 core KPIs with SQL queries |
| ML Predictions | `backend/nlp/ml_predictions_library.py` | 9 ML prediction tables |
| Query Learning | `backend/nlp/query_learning.py` | Captures successful queries for reuse |
| Feedback System | `backend/nlp/feedback_system.py` | Stores user feedback on responses |
| Response Generator | `backend/nlp/response_generator.py` | Formats output with charts/tables |
| Context Manager | `backend/nlp/context_manager_v2.py` | Conversation memory |
| SQL Templates | `backend/nlp/sql_templates/*.py` | ~80 predefined query templates |

### Frontend Components
| Component | File | Purpose |
|-----------|------|---------|
| Chat Interface | `frontend/components/ChatInterface.tsx` | Main chat UI |
| Chat Message | `frontend/components/ChatMessage.tsx` | Message rendering with markdown |
| Feedback Buttons | `frontend/components/FeedbackButtons.tsx` | ✓/✗ feedback buttons |
| Inline Chart | `frontend/components/InlineChart.tsx` | Chart rendering (bar, line, pie) |

---

## Enhancement Plan

### 1. Questions Library (1000+ Predefined Questions)

**Approach:** Hybrid - AI-generated variations from curated base templates

#### Structure
```
backend/nlp/questions_library/
├── __init__.py                 # Main exports & registry
├── base_templates.py           # Core question patterns
├── kpi_questions.py            # 100+ KPI variations
├── analytics_questions.py      # 300+ analytics patterns
├── prediction_questions.py     # 200+ ML/forecasting
├── comparison_questions.py     # 150+ comparative analytics
├── temporal_questions.py       # 100+ time-based patterns
├── entity_questions.py         # 150+ entity-specific queries
└── generated_variations.py     # AI-generated variations
```

#### Question Template Structure
```python
@dataclass
class QuestionTemplate:
    id: str                          # Unique identifier (e.g., "KPI_COMP_001")
    category: str                    # "kpi", "analytics", "prediction", "comparison"
    subcategory: str                 # "violations", "inspectors", "compliance"
    intent: List[str]                # ["COUNT", "TREND", "COMPARE"]
    
    # Bilingual support
    question_en: str                 # Primary English question
    question_ar: str                 # Primary Arabic question
    variations_en: List[str]         # Alternative phrasings (EN)
    variations_ar: List[str]         # Alternative phrasings (AR)
    keywords_en: List[str]           # Semantic matching keywords
    keywords_ar: List[str]           
    
    # Query configuration
    sql: str                         # SQL query with placeholders
    parameters: Dict[str, type]      # {year: int, location: str}
    default_values: Dict[str, Any]   # Default parameter values
    
    # Output configuration
    output_format: str               # "table", "chart", "both", "calculation"
    chart_type: str                  # "bar", "line", "pie", "heatmap", "sankey"
    calculation_steps: bool          # Show step-by-step math
    
    # Metadata
    difficulty: str                  # "basic", "intermediate", "advanced"
    usage_count: int                 # Track popularity
    success_rate: float              # Track accuracy
```

#### Category Breakdown

| Category | Subcategories | Count | Examples |
|----------|---------------|-------|----------|
| **KPIs** | Compliance, Performance, Violations, Risk, Efficiency | 100 | "What is the compliance rate?", "Show KPI dashboard" |
| **Analytics** | Trends, Rankings, Distributions, Aggregates, Patterns | 300 | "Top 10 violation types", "Distribution by severity" |
| **Predictions** | Forecasting, Risk Scoring, Anomalies, Scheduling | 200 | "Predicted violations next month", "High-risk locations" |
| **Comparisons** | Time Periods, Locations, Inspectors, Categories | 150 | "Compare 2024 vs 2023", "Riyadh vs Jeddah violations" |
| **Temporal** | Daily, Weekly, Monthly, Quarterly, Yearly, Seasonal | 100 | "Monthly trend", "Busiest inspection days" |
| **Entity-Based** | Inspectors, Locations, Violations, Events, Organizations | 150 | "Inspector X performance", "Location Y history" |
| **Total** | | **1,000+** | |

#### AI Variation Generation
```python
class VariationGenerator:
    """Uses Claude to generate question variations from base templates."""
    
    def generate_variations(self, base_question: str, count: int = 10) -> List[str]:
        prompt = f"""
        Generate {count} natural language variations of this question:
        "{base_question}"
        
        Rules:
        - Keep the same intent and expected result
        - Use different phrasings, synonyms, and structures
        - Include formal and informal versions
        - Include abbreviated versions
        """
        return self.claude_client.generate(prompt)
    
    def batch_generate(self, templates: List[QuestionTemplate]) -> None:
        """Generate variations for all base templates."""
        for template in templates:
            template.variations_en = self.generate_variations(template.question_en)
            template.variations_ar = self.generate_variations(template.question_ar)
```

---

### 2. Enhanced Feedback UI (👍/👎 Icons)

**Approach:** Replace ✓/✗ buttons with thumbs icons + granular feedback options

#### Updated FeedbackButtons Component
```typescript
// frontend/components/FeedbackButtons.tsx

import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface FeedbackData {
  messageId: string;
  rating: 'correct' | 'partial' | 'incorrect';
  issues?: {
    data_wrong?: boolean;
    format_wrong?: boolean;
    incomplete?: boolean;
    wrong_chart?: boolean;
    too_slow?: boolean;
  };
  clarification?: string;
  expected_result?: string;
  correct_sql?: string;  // For power users
}

export function FeedbackButtons({ messageId, onFeedback }: Props) {
  const [showDetails, setShowDetails] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackData | null>(null);

  return (
    <div className="feedback-container">
      {/* Primary feedback buttons */}
      <div className="flex gap-2">
        <button 
          onClick={() => handlePositive()}
          className="hover:bg-green-100 p-2 rounded-full"
          title="Correct response"
        >
          <ThumbsUp className="w-5 h-5 text-green-600" />
        </button>
        <button 
          onClick={() => setShowDetails(true)}
          className="hover:bg-red-100 p-2 rounded-full"
          title="Incorrect response"
        >
          <ThumbsDown className="w-5 h-5 text-red-600" />
        </button>
      </div>

      {/* Detailed feedback panel (shown on thumbs down) */}
      {showDetails && (
        <FeedbackDetailsPanel
          onSubmit={handleDetailedFeedback}
          onCancel={() => setShowDetails(false)}
        />
      )}
    </div>
  );
}

function FeedbackDetailsPanel({ onSubmit, onCancel }: PanelProps) {
  return (
    <div className="bg-gray-50 p-4 rounded-lg mt-2 border">
      <h4 className="font-semibold mb-2">What was wrong?</h4>
      
      {/* Issue checkboxes */}
      <div className="space-y-2 mb-4">
        <Checkbox id="data_wrong" label="Data/numbers are incorrect" />
        <Checkbox id="format_wrong" label="Wrong format/visualization" />
        <Checkbox id="incomplete" label="Missing information" />
        <Checkbox id="wrong_chart" label="Wrong chart type" />
        <Checkbox id="too_slow" label="Response was too slow" />
      </div>

      {/* Clarification text */}
      <textarea
        placeholder="Describe what you expected or how to fix it..."
        className="w-full p-2 border rounded mb-2"
        rows={3}
      />

      {/* Expected result (optional) */}
      <input
        type="text"
        placeholder="Expected result (optional)"
        className="w-full p-2 border rounded mb-4"
      />

      <div className="flex gap-2">
        <button onClick={onSubmit} className="bg-blue-600 text-white px-4 py-2 rounded">
          Submit Feedback
        </button>
        <button onClick={onCancel} className="text-gray-600 px-4 py-2">
          Cancel
        </button>
      </div>
    </div>
  );
}
```

#### Backend API Update
```python
# backend/nlp/feedback_system.py

@dataclass
class EnhancedFeedback:
    message_id: str
    question: str
    sql_query: str
    response_data: Any
    
    # Feedback details
    rating: Literal['correct', 'partial', 'incorrect']
    issues: Dict[str, bool] = field(default_factory=dict)
    clarification: Optional[str] = None
    expected_result: Optional[str] = None
    correct_sql: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class EnhancedFeedbackSystem:
    def __init__(self):
        self.storage = FeedbackStorage()  # PostgreSQL for production
        self.learning_system = QueryLearningSystem()
        self.correction_learner = CorrectionLearner()
    
    async def submit_feedback(self, feedback: EnhancedFeedback) -> Dict:
        # Store feedback
        await self.storage.save(feedback)
        
        # If incorrect, trigger learning
        if feedback.rating in ['partial', 'incorrect']:
            correction = await self.correction_learner.learn_from_feedback(feedback)
            return {
                "status": "received",
                "correction_generated": correction is not None,
                "new_response": correction.response if correction else None
            }
        
        # If correct, reinforce the query
        if feedback.rating == 'correct':
            await self.learning_system.reinforce_query(
                question=feedback.question,
                sql=feedback.sql_query,
                user_validated=True
            )
        
        return {"status": "received"}
```

---

### 3. Correction Learning System

**Approach:** Store in PostgreSQL (production) with SQLite fallback, export to files for training

#### Architecture
```python
# backend/nlp/correction_learner.py

class CorrectionLearner:
    """Learns from user corrections to improve query generation."""
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.learning_system = QueryLearningSystem()
        self.error_tracker = ErrorPatternTracker()
        self.storage = CorrectionStorage()
    
    async def learn_from_feedback(self, feedback: EnhancedFeedback) -> Optional[Correction]:
        """Process negative feedback and generate correction."""
        
        # 1. Analyze what went wrong
        error_analysis = await self.analyze_error(
            original_question=feedback.question,
            failed_sql=feedback.sql_query,
            issues=feedback.issues,
            clarification=feedback.clarification
        )
        
        # 2. Generate corrected SQL using Claude with context
        corrected_sql = await self.generate_correction(
            question=feedback.question,
            failed_sql=feedback.sql_query,
            error_analysis=error_analysis,
            user_clarification=feedback.clarification,
            expected_result=feedback.expected_result
        )
        
        if corrected_sql:
            # 3. Execute and validate the correction
            result = await self.execute_and_validate(corrected_sql)
            
            if result.success:
                # 4. Store as learned pattern with HIGH confidence
                await self.learning_system.capture_query(
                    question=feedback.question,
                    sql=corrected_sql,
                    user_validated=True,
                    correction_source=True,
                    confidence=0.95  # High confidence for corrections
                )
                
                # 5. Track error pattern for future prevention
                await self.error_tracker.record_pattern(
                    error_type=error_analysis.error_type,
                    wrong_sql=feedback.sql_query,
                    correct_sql=corrected_sql,
                    context=error_analysis.context
                )
                
                return Correction(
                    original_sql=feedback.sql_query,
                    corrected_sql=corrected_sql,
                    response=result.formatted_response
                )
        
        return None
    
    async def analyze_error(self, **kwargs) -> ErrorAnalysis:
        """Use Claude to analyze what went wrong."""
        prompt = f"""
        Analyze this failed query:
        
        Question: {kwargs['original_question']}
        SQL Used: {kwargs['failed_sql']}
        User Issues: {kwargs['issues']}
        User Clarification: {kwargs['clarification']}
        
        Identify:
        1. Error type (wrong_table, wrong_column, wrong_aggregation, wrong_filter, wrong_join)
        2. Specific issue
        3. Suggested fix
        """
        return await self.claude_client.analyze(prompt)
    
    async def generate_correction(self, **kwargs) -> Optional[str]:
        """Generate corrected SQL based on feedback."""
        prompt = f"""
        Generate a corrected SQL query:
        
        Original Question: {kwargs['question']}
        Failed SQL: {kwargs['failed_sql']}
        Error Analysis: {kwargs['error_analysis']}
        User Clarification: {kwargs['user_clarification']}
        Expected Result: {kwargs['expected_result']}
        
        Return ONLY the corrected SQL query.
        """
        return await self.claude_client.generate_sql(prompt)


class ErrorPatternTracker:
    """Tracks error patterns to prevent future mistakes."""
    
    def __init__(self):
        self.patterns = {}  # error_type -> [patterns]
    
    async def record_pattern(self, error_type: str, wrong_sql: str, 
                            correct_sql: str, context: Dict):
        """Store error pattern for learning."""
        pattern = ErrorPattern(
            error_type=error_type,
            wrong_pattern=self.extract_pattern(wrong_sql),
            correct_pattern=self.extract_pattern(correct_sql),
            context=context,
            timestamp=datetime.now()
        )
        await self.storage.save(pattern)
    
    def get_prevention_hints(self, question: str) -> List[str]:
        """Get hints to prevent known errors for similar questions."""
        similar_errors = self.find_similar_patterns(question)
        return [e.prevention_hint for e in similar_errors]
```

#### Storage Configuration
```python
# backend/nlp/storage/correction_storage.py

class CorrectionStorage:
    """Hybrid storage: PostgreSQL primary, SQLite fallback, file export for training."""
    
    def __init__(self):
        self.primary = PostgreSQLStorage()  # Production
        self.fallback = SQLiteStorage()     # Local/fallback
        self.export_path = Path("data/training_exports/")
    
    async def save(self, correction: Correction):
        try:
            await self.primary.save(correction)
        except ConnectionError:
            await self.fallback.save(correction)
    
    def export_for_training(self, start_date: datetime, end_date: datetime) -> Path:
        """Export corrections to JSON/CSV for model training."""
        corrections = self.get_range(start_date, end_date)
        
        export_file = self.export_path / f"corrections_{start_date}_{end_date}.json"
        with open(export_file, 'w') as f:
            json.dump([c.to_dict() for c in corrections], f, indent=2)
        
        return export_file
```

---

### 4. Output Formatting Enhancement

**Approach:** Enhance response_generator.py + add D3.js for advanced visualizations

#### Enhanced Response Generator
```python
# backend/nlp/response_generator.py

class EnhancedResponseGenerator:
    """Generates rich, formatted responses with multiple output types."""
    
    def generate_response(self, data: QueryResult, config: OutputConfig) -> FormattedResponse:
        return FormattedResponse(
            # Text summary
            summary=self.generate_summary(data),
            summary_ar=self.generate_summary_ar(data),
            
            # Tabular data
            table=self.format_table(data, config.table_config),
            
            # Visualization
            chart=self.generate_chart(data, config.chart_type),
            diagram=self.generate_diagram(data, config.diagram_type),  # NEW
            
            # Calculations
            calculations=self.show_calculations(data, config.show_steps),  # NEW
            
            # Insights
            insights=self.generate_insights(data),  # NEW
            
            # Context
            recommendations=self.get_recommendations(data),
            follow_up_suggestions=self.get_follow_ups(data),  # NEW
            
            # Export
            export_options=self.get_export_options(data)
        )
    
    def show_calculations(self, data: QueryResult, show_steps: bool) -> Optional[CalculationDisplay]:
        """Show step-by-step calculations for aggregations."""
        if not show_steps or not data.has_aggregation:
            return None
        
        steps = []
        if data.aggregation_type == "average":
            steps = [
                f"Sum of values: {data.sum}",
                f"Count of records: {data.count}",
                f"Average = {data.sum} / {data.count} = {data.result}"
            ]
        elif data.aggregation_type == "percentage":
            steps = [
                f"Numerator (matching): {data.numerator}",
                f"Denominator (total): {data.denominator}",
                f"Percentage = ({data.numerator} / {data.denominator}) × 100 = {data.result}%"
            ]
        # ... more calculation types
        
        return CalculationDisplay(
            formula=data.formula,
            steps=steps,
            result=data.result,
            unit=data.unit
        )
    
    def generate_diagram(self, data: QueryResult, diagram_type: str) -> Optional[DiagramConfig]:
        """Generate configuration for advanced diagrams."""
        if diagram_type == "sankey":
            return self.create_sankey_config(data)
        elif diagram_type == "treemap":
            return self.create_treemap_config(data)
        elif diagram_type == "heatmap":
            return self.create_heatmap_config(data)
        elif diagram_type == "funnel":
            return self.create_funnel_config(data)
        elif diagram_type == "gauge":
            return self.create_gauge_config(data)
        return None
    
    def create_sankey_config(self, data: QueryResult) -> DiagramConfig:
        """Create Sankey diagram for flow visualization."""
        # Example: Violation flow from detection → investigation → resolution
        return DiagramConfig(
            type="sankey",
            data={
                "nodes": [
                    {"id": "detected", "name": "Detected"},
                    {"id": "investigating", "name": "Investigating"},
                    {"id": "resolved", "name": "Resolved"},
                    {"id": "escalated", "name": "Escalated"}
                ],
                "links": data.flow_links
            },
            options={
                "nodeWidth": 15,
                "nodePadding": 10,
                "colors": ALULA_BRAND_COLORS
            }
        )
```

#### Frontend D3.js Integration
```typescript
// frontend/components/AdvancedChart.tsx

import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';

interface AdvancedChartProps {
  type: 'sankey' | 'treemap' | 'heatmap' | 'funnel' | 'gauge';
  data: any;
  config: DiagramConfig;
}

export function AdvancedChart({ type, data, config }: AdvancedChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();  // Clear previous

    switch (type) {
      case 'sankey':
        renderSankey(svg, data, config);
        break;
      case 'treemap':
        renderTreemap(svg, data, config);
        break;
      case 'heatmap':
        renderHeatmap(svg, data, config);
        break;
      case 'funnel':
        renderFunnel(svg, data, config);
        break;
      case 'gauge':
        renderGauge(svg, data, config);
        break;
    }
  }, [type, data, config]);

  return <svg ref={svgRef} width={config.width} height={config.height} />;
}

function renderSankey(svg: d3.Selection, data: SankeyData, config: DiagramConfig) {
  const { width, height } = config;
  
  const sankeyGenerator = sankey()
    .nodeWidth(config.options.nodeWidth)
    .nodePadding(config.options.nodePadding)
    .extent([[1, 1], [width - 1, height - 5]]);

  const { nodes, links } = sankeyGenerator({
    nodes: data.nodes.map(d => ({ ...d })),
    links: data.links.map(d => ({ ...d }))
  });

  // Draw links
  svg.append("g")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("d", sankeyLinkHorizontal())
    .attr("fill", "none")
    .attr("stroke", d => config.options.colors[d.source.index % config.options.colors.length])
    .attr("stroke-opacity", 0.5)
    .attr("stroke-width", d => Math.max(1, d.width));

  // Draw nodes
  svg.append("g")
    .selectAll("rect")
    .data(nodes)
    .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("height", d => d.y1 - d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("fill", d => config.options.colors[d.index % config.options.colors.length]);

  // Add labels
  svg.append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
    .attr("y", d => (d.y1 + d.y0) / 2)
    .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
    .text(d => d.name);
}

// Similar implementations for treemap, heatmap, funnel, gauge...
```

#### Calculation Display Component
```typescript
// frontend/components/CalculationDisplay.tsx

interface CalculationDisplayProps {
  formula: string;
  steps: string[];
  result: number | string;
  unit?: string;
}

export function CalculationDisplay({ formula, steps, result, unit }: CalculationDisplayProps) {
  return (
    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
      <h4 className="font-semibold text-blue-800 mb-2">📊 Calculation</h4>
      
      {/* Formula */}
      <div className="font-mono bg-white p-2 rounded mb-3">
        {formula}
      </div>
      
      {/* Steps */}
      <div className="space-y-1 mb-3">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-2">
            <span className="text-blue-600 font-bold">{index + 1}.</span>
            <span className="font-mono text-sm">{step}</span>
          </div>
        ))}
      </div>
      
      {/* Result */}
      <div className="bg-green-100 p-2 rounded text-center">
        <span className="text-2xl font-bold text-green-800">
          {result}{unit && ` ${unit}`}
        </span>
      </div>
    </div>
  );
}
```

---

### 5. Smart Contextual Suggestions

**Approach:** Extend context_manager_v2.py with user preference tracking and smart follow-ups

#### Enhanced Context Manager
```python
# backend/nlp/context_manager_v2.py

class EnhancedContextManager:
    """Manages conversation context with user preferences and smart suggestions."""
    
    def __init__(self):
        self.sessions = {}  # session_id -> SessionContext
        self.user_profiles = {}  # user_id -> UserPreferences
    
    def get_session_context(self, session_id: str) -> SessionContext:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(session_id)
        return self.sessions[session_id]
    
    def update_context(self, session_id: str, message: Message, response: Response):
        """Update context after each interaction."""
        ctx = self.get_session_context(session_id)
        
        # Track entities mentioned
        ctx.last_entities = response.entities_mentioned
        ctx.entity_history.extend(response.entities_mentioned)
        
        # Track time ranges
        if response.time_range:
            ctx.last_time_range = response.time_range
            ctx.time_range_history.append(response.time_range)
        
        # Track metrics/KPIs discussed
        ctx.last_metrics = response.metrics_used
        
        # Track visualization preferences
        if response.chart_type:
            ctx.preferred_chart_types.append(response.chart_type)
        
        # Update conversation history
        ctx.history.append({
            "question": message.content,
            "response_summary": response.summary,
            "entities": response.entities_mentioned,
            "time_range": response.time_range,
            "timestamp": datetime.now()
        })
    
    def get_follow_up_suggestions(self, session_id: str, current_response: Response) -> List[Suggestion]:
        """Generate smart follow-up suggestions based on context."""
        ctx = self.get_session_context(session_id)
        suggestions = []
        
        # Drill-down suggestions
        if current_response.has_aggregation:
            for entity in current_response.drilldown_options:
                suggestions.append(Suggestion(
                    text=f"Break down by {entity}",
                    text_ar=f"تفصيل حسب {entity}",
                    type="drill_down",
                    icon="zoom-in",
                    query_hint=f"breakdown by {entity}"
                ))
        
        # Time comparison suggestions
        if ctx.last_time_range:
            prev_period = self.get_previous_period(ctx.last_time_range)
            suggestions.append(Suggestion(
                text=f"Compare with {prev_period}",
                text_ar=f"مقارنة مع {prev_period}",
                type="comparison",
                icon="git-compare",
                query_hint=f"compare with {prev_period}"
            ))
        
        # Prediction suggestions
        if current_response.category in ["violations", "inspections", "compliance"]:
            suggestions.append(Suggestion(
                text="Show prediction for next period",
                text_ar="عرض التوقعات للفترة القادمة",
                type="prediction",
                icon="trending-up",
                query_hint="predict next period"
            ))
        
        # Related entity suggestions
        for entity in current_response.related_entities[:3]:
            suggestions.append(Suggestion(
                text=f"Show details for {entity}",
                text_ar=f"عرض تفاصيل {entity}",
                type="entity_detail",
                icon="info",
                query_hint=f"details for {entity}"
            ))
        
        # Visualization change suggestions
        alt_charts = self.get_alternative_charts(current_response.chart_type)
        for chart in alt_charts[:2]:
            suggestions.append(Suggestion(
                text=f"Show as {chart}",
                text_ar=f"عرض كـ {chart}",
                type="visualization",
                icon="bar-chart",
                query_hint=f"show as {chart}"
            ))
        
        return suggestions[:6]  # Limit to 6 suggestions


@dataclass
class Suggestion:
    text: str
    text_ar: str
    type: str  # drill_down, comparison, prediction, entity_detail, visualization
    icon: str
    query_hint: str
    confidence: float = 0.8


@dataclass
class SessionContext:
    session_id: str
    history: List[Dict] = field(default_factory=list)
    
    # Last interaction context
    last_entities: List[str] = field(default_factory=list)
    last_time_range: Optional[TimeRange] = None
    last_metrics: List[str] = field(default_factory=list)
    
    # Accumulated preferences
    entity_history: List[str] = field(default_factory=list)
    time_range_history: List[TimeRange] = field(default_factory=list)
    preferred_chart_types: List[str] = field(default_factory=list)
    
    # User language preference
    language: str = "en"
```

#### Frontend Suggestions Component
```typescript
// frontend/components/SuggestionChips.tsx

import { ZoomIn, GitCompare, TrendingUp, Info, BarChart2 } from 'lucide-react';

interface Suggestion {
  text: string;
  text_ar: string;
  type: string;
  icon: string;
  query_hint: string;
}

interface SuggestionChipsProps {
  suggestions: Suggestion[];
  language: 'en' | 'ar';
  onSelect: (query: string) => void;
}

const iconMap = {
  'zoom-in': ZoomIn,
  'git-compare': GitCompare,
  'trending-up': TrendingUp,
  'info': Info,
  'bar-chart': BarChart2,
};

export function SuggestionChips({ suggestions, language, onSelect }: SuggestionChipsProps) {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {suggestions.map((suggestion, index) => {
        const Icon = iconMap[suggestion.icon] || Info;
        const text = language === 'ar' ? suggestion.text_ar : suggestion.text;
        
        return (
          <button
            key={index}
            onClick={() => onSelect(suggestion.query_hint)}
            className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 
                       rounded-full text-sm text-gray-700 transition-colors"
          >
            <Icon className="w-4 h-4" />
            <span>{text}</span>
          </button>
        );
      })}
    </div>
  );
}
```

---

### 6. Natural Follow-up Understanding

**Approach:** Enhance chat_agent_v2.py with reference resolution using conversation context

#### Reference Resolution System
```python
# backend/nlp/reference_resolver.py

class ReferenceResolver:
    """Resolves natural language references using conversation context."""
    
    def __init__(self):
        self.time_references = {
            "last year": lambda ctx: self.shift_year(ctx.last_time_range, -1),
            "previous year": lambda ctx: self.shift_year(ctx.last_time_range, -1),
            "next year": lambda ctx: self.shift_year(ctx.last_time_range, 1),
            "last month": lambda ctx: self.shift_month(ctx.last_time_range, -1),
            "this month": lambda ctx: TimeRange.current_month(),
            "yesterday": lambda ctx: TimeRange.yesterday(),
            "last week": lambda ctx: self.shift_week(ctx.last_time_range, -1),
            "same period last year": lambda ctx: self.same_period_prev_year(ctx.last_time_range),
        }
        
        self.pronoun_references = {
            "it": lambda ctx: ctx.last_entities[0] if ctx.last_entities else None,
            "them": lambda ctx: ctx.last_entities,
            "that": lambda ctx: ctx.last_entities[0] if ctx.last_entities else None,
            "those": lambda ctx: ctx.last_entities,
            "this location": lambda ctx: self.get_last_entity_of_type(ctx, "location"),
            "this inspector": lambda ctx: self.get_last_entity_of_type(ctx, "inspector"),
            "these violations": lambda ctx: self.get_last_entity_of_type(ctx, "violation"),
        }
        
        self.action_references = {
            "break it down": "breakdown",
            "break down": "breakdown",
            "drill down": "drilldown",
            "show more": "expand",
            "show less": "collapse",
            "top 5": lambda ctx: f"top 5 {ctx.last_metrics[0]}" if ctx.last_metrics else "top 5",
            "top 10": lambda ctx: f"top 10 {ctx.last_metrics[0]}" if ctx.last_metrics else "top 10",
            "by month": "group by month",
            "by week": "group by week",
            "by location": "group by location",
            "by inspector": "group by inspector",
        }
    
    def resolve(self, query: str, context: SessionContext) -> ResolvedQuery:
        """Resolve all references in a query using context."""
        resolved_query = query
        resolutions = []
        
        # Resolve time references
        for ref, resolver in self.time_references.items():
            if ref in query.lower():
                time_range = resolver(context)
                if time_range:
                    resolved_query = self.replace_time_ref(resolved_query, ref, time_range)
                    resolutions.append(Resolution("time", ref, str(time_range)))
        
        # Resolve pronoun references
        for ref, resolver in self.pronoun_references.items():
            if ref in query.lower():
                entity = resolver(context)
                if entity:
                    resolved_query = resolved_query.replace(ref, str(entity))
                    resolutions.append(Resolution("entity", ref, str(entity)))
        
        # Resolve action references
        for ref, action in self.action_references.items():
            if ref in query.lower():
                if callable(action):
                    action = action(context)
                resolved_query = self.apply_action(resolved_query, ref, action, context)
                resolutions.append(Resolution("action", ref, action))
        
        return ResolvedQuery(
            original=query,
            resolved=resolved_query,
            resolutions=resolutions,
            context_used=True if resolutions else False
        )


# Integration in chat_agent_v2.py

class IntelligentChatAgent:
    def __init__(self):
        # ... existing initialization
        self.reference_resolver = ReferenceResolver()
    
    async def process_message(self, message: str, session_id: str) -> Response:
        # Get conversation context
        context = self.context_manager.get_session_context(session_id)
        
        # Resolve references before processing
        resolved = self.reference_resolver.resolve(message, context)
        
        if resolved.context_used:
            logger.info(f"Resolved references: {resolved.resolutions}")
        
        # Continue with resolved query
        query_to_process = resolved.resolved
        
        # ... rest of processing pipeline
```

#### Example Conversations

```
User: "How many violations in 2024?"
→ AI responds with: 15,234 violations in 2024

User: "What about last year?"
→ Resolved: "What about 2023?" (using context)
→ AI responds with: 12,891 violations in 2023

User: "Break it down by month"
→ Resolved: "Break down violations in 2023 by month"
→ AI shows monthly chart

User: "Show me the top 5 locations"
→ Resolved: "Show me the top 5 locations by violations in 2023"
→ AI shows top 5 locations

User: "Compare with 2024"
→ Resolved: "Compare top 5 locations by violations 2023 vs 2024"
→ AI shows comparison chart
```

---

## Implementation Timeline

| Week | Phase | Tasks |
|------|-------|-------|
| 1-2 | **Foundation** | Create questions library structure, generate 500+ base templates |
| 2-3 | **Feedback UI** | Implement 👍/👎 icons, granular feedback panel, API integration |
| 3-4 | **Correction Learning** | Build CorrectionLearner, ErrorPatternTracker, PostgreSQL storage |
| 4-5 | **Output Formatting** | Enhanced response generator, D3.js integration, calculation display |
| 5-6 | **Smart Suggestions** | Context manager enhancements, suggestion chips UI |
| 6-7 | **Reference Resolution** | Natural follow-up understanding, conversation memory |
| 7-8 | **Testing & Polish** | Integration testing, performance optimization, documentation |

---

## Files to Create/Modify

### New Files
| Path | Purpose |
|------|---------|
| `backend/nlp/questions_library/__init__.py` | Question library registry |
| `backend/nlp/questions_library/base_templates.py` | Core question patterns |
| `backend/nlp/questions_library/kpi_questions.py` | KPI variations (100+) |
| `backend/nlp/questions_library/analytics_questions.py` | Analytics patterns (300+) |
| `backend/nlp/questions_library/prediction_questions.py` | ML/forecasting (200+) |
| `backend/nlp/questions_library/comparison_questions.py` | Comparisons (150+) |
| `backend/nlp/questions_library/temporal_questions.py` | Time-based (100+) |
| `backend/nlp/questions_library/entity_questions.py` | Entity-specific (150+) |
| `backend/nlp/correction_learner.py` | Correction learning system |
| `backend/nlp/reference_resolver.py` | Natural language reference resolution |
| `frontend/components/AdvancedChart.tsx` | D3.js advanced visualizations |
| `frontend/components/CalculationDisplay.tsx` | Step-by-step calculations |
| `frontend/components/SuggestionChips.tsx` | Follow-up suggestions UI |

### Modified Files
| Path | Changes |
|------|---------|
| `backend/nlp/kpi_library.py` | Expand to 100+ KPIs |
| `backend/nlp/feedback_system.py` | Add granular feedback, correction integration |
| `backend/nlp/query_learning.py` | Add correction learning hooks |
| `backend/nlp/response_generator.py` | Add calculations, diagrams, insights |
| `backend/nlp/context_manager_v2.py` | Add preference tracking, smart suggestions |
| `backend/nlp/chat_agent_v2.py` | Integrate reference resolver |
| `frontend/components/FeedbackButtons.tsx` | 👍/👎 icons, detailed feedback panel |
| `frontend/components/ChatMessage.tsx` | Render calculations, advanced charts |
| `frontend/components/ChatInterface.tsx` | Integrate suggestion chips |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Questions covered | ~100 | 1,000+ |
| User feedback rate | 5% | 25% |
| Query correction success | N/A | 80%+ |
| Follow-up understanding | Limited | 90%+ accuracy |
| User satisfaction | Unknown | 4.5/5 rating |

---

## Appendix: Sample Question Categories

### KPI Questions (Sample)
1. What is the current compliance rate?
2. How many active inspectors do we have?
3. What is the average inspection score this month?
4. Show KPI dashboard
5. What is the violation resolution rate?

### Analytics Questions (Sample)
1. Top 10 violation types by frequency
2. Distribution of inspections by severity
3. Monthly trend of violations
4. Inspector performance ranking
5. Geographic distribution of issues

### Prediction Questions (Sample)
1. Predicted violations for next month
2. High-risk locations forecast
3. Anomaly detection results
4. Scheduling recommendations
5. Risk score predictions

### Comparison Questions (Sample)
1. Compare 2024 vs 2023 violations
2. Riyadh vs Jeddah inspection rates
3. Inspector A vs Inspector B performance
4. This quarter vs last quarter compliance
5. Before/after comparison for location X

---

## Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Question Library Generation | **Hybrid** (AI + Manual) | Best balance of coverage and quality |
| Feedback Data Storage | **PostgreSQL** (primary) + SQLite (fallback) + File export | Production reliability with training data export |
| Visualization Library | **Recharts + D3.js** | Recharts for standard charts, D3.js for advanced diagrams |
