# AlUla Inspection AI - 4D Analysis Framework

## Overview

The AlUla Inspection AI Chatbot implements a powerful **4-Dimensional Analysis Framework** that goes beyond simple data retrieval to provide deep, actionable insights. This framework enables users to ask complex analytical questions in both Arabic and English and receive intelligent, multi-faceted answers.

**Total Templates:** 50 specialized analysis queries

---

## The 4 Dimensions

### 1️⃣ Dimension 1: Correlation Analysis (15 Templates)

**Purpose:** Find relationships and connections between different metrics

**What it does:**
- Discovers patterns like "Do inspectors with higher workloads find more violations?"
- Identifies relationships between inspection duration and quality scores
- Reveals connections between location types and violation severity
- Analyzes day-of-week and seasonal impacts on inspection outcomes

#### Sample Questions

| English | العربية |
|---------|---------|
| What's the relationship between inspector workload and violations? | ما العلاقة بين حجم عمل المفتش وعدد المخالفات؟ |
| Is there a correlation between inspection duration and quality? | هل هناك ارتباط بين مدة التفتيش والجودة؟ |
| Which days of the week have the most violations? | أي أيام الأسبوع لديها أكثر المخالفات؟ |
| Show seasonal inspection patterns | أظهر أنماط التفتيش الموسمية |
| How do critical issues affect overall scores? | كيف تؤثر المشاكل الحرجة على الدرجة الإجمالية؟ |

#### Available Templates

| ID | Template Name (EN) | Template Name (AR) | Chart Type |
|----|-------------------|-------------------|------------|
| COR_01 | Violations vs Inspector Workload Correlation | ارتباط المخالفات بحجم عمل المفتش | Scatter |
| COR_02 | Location Type vs Violation Severity | نوع الموقع مقابل خطورة المخالفة | Bar |
| COR_03 | Inspection Duration vs Quality Score | مدة التفتيش مقابل جودة النتيجة | Scatter |
| COR_04 | Monthly Violation Type Patterns | أنماط أنواع المخالفات الشهرية | Line |
| COR_05 | Repeat Violations by Location | المخالفات المتكررة حسب الموقع | Bar |
| COR_06 | Day of Week Impact Analysis | تحليل تأثير يوم الأسبوع | Bar |
| COR_07 | Objection Rate by Violation Type | معدل الاعتراض حسب نوع المخالفة | Bar |
| COR_08 | Critical Issues vs Overall Score | المشاكل الحرجة مقابل الدرجة الإجمالية | Scatter |
| COR_09 | Seasonal Inspection Patterns | أنماط التفتيش الموسمية | Area |
| COR_10 | Severity Distribution by Location Type | توزيع الخطورة حسب نوع الموقع | Bar |
| COR_11 | Inspector Experience vs Efficiency | خبرة المفتش مقابل الكفاءة | Scatter |
| COR_12 | Violation Value vs Objection Rate | قيمة المخالفة مقابل معدل الاعتراض | Scatter |
| COR_13 | Time of Day Violation Patterns | أنماط المخالفات حسب وقت اليوم | Line |
| COR_14 | Neighborhood Risk Clustering | تجميع مخاطر الأحياء | Bar |
| COR_15 | Multi-Factor Performance Index | مؤشر الأداء متعدد العوامل | Composed |

---

### 2️⃣ Dimension 2: Anomaly Detection (12 Templates)

**Purpose:** Identify unusual patterns, outliers, and suspicious activities

**What it does:**
- Uses statistical methods (standard deviation) to detect spikes and drops
- Flags locations with unusually high or low violation rates
- Identifies inspector performance outliers
- Detects suspicious patterns like "perfect 100% scores" or "zero violations consistently"

#### Statistical Method Used
```
High Anomaly:   value > average + 2 × standard_deviation
Elevated:       value > average + 1 × standard_deviation  
Normal:         within ±1 standard deviation
Low Anomaly:    value < average - 1 × standard_deviation
```

#### Sample Questions

| English | العربية |
|---------|---------|
| Detect locations with unusual activity | اكتشف المواقع ذات النشاط غير العادي |
| Which inspectors have outlier performance? | أي المفتشين لديهم أداء متطرف؟ |
| Are there any violation spikes this year? | هل هناك ارتفاعات في المخالفات هذا العام؟ |
| Show me suspicious perfect scores | أظهر لي الدرجات المثالية المشبوهة |
| Which locations haven't been inspected recently? | أي المواقع لم يتم تفتيشها مؤخراً؟ |
| Find inspectors with suspiciously clean records | ابحث عن مفتشين بسجلات نظيفة بشكل مريب |

#### Available Templates

| ID | Template Name (EN) | Template Name (AR) | Chart Type |
|----|-------------------|-------------------|------------|
| ANO_01 | Violation Spikes Detection | اكتشاف ارتفاعات المخالفات | Line |
| ANO_02 | Locations with Unusual Activity | مواقع بنشاط غير عادي | Bar |
| ANO_03 | Inspector Performance Outliers | المفتشون ذوو الأداء المتطرف | Bar |
| ANO_04 | Suspiciously Clean Records | سجلات نظيفة بشكل مريب | Bar |
| ANO_05 | Unusual Inspection Duration | مدة تفتيش غير عادية | Bar |
| ANO_06 | Score Distribution Anomalies | شذوذ توزيع الدرجات | Bar |
| ANO_07 | Perfect Score Patterns | أنماط الدرجات المثالية | Bar |
| ANO_08 | Inactive Location Detection | اكتشاف المواقع غير النشطة | Bar |
| ANO_09 | Violation Rate Extremes | تطرفات معدل المخالفات | Bar |
| ANO_10 | Seasonal Anomaly Detection | اكتشاف الشذوذ الموسمي | Line |
| ANO_11 | Inspector Activity Gaps | فجوات نشاط المفتش | Bar |
| ANO_12 | Sudden Compliance Changes | تغييرات الامتثال المفاجئة | Line |

---

### 3️⃣ Dimension 3: Comparative Analysis (12 Templates)

**Purpose:** Compare performance across different dimensions and time periods

**What it does:**
- Compares neighborhoods against each other
- Benchmarks inspector performance
- Analyzes year-over-year, quarter-over-quarter, and month-over-month trends
- Identifies best vs worst performing entities
- Shows distribution and percentage breakdowns

#### Sample Questions

| English | العربية |
|---------|---------|
| Compare neighborhood performance | قارن أداء الأحياء |
| How does Q1 compare to Q2 this year? | كيف يقارن الربع الأول بالربع الثاني هذا العام؟ |
| Show top vs bottom performing locations | أظهر المواقع الأفضل مقابل الأسوأ أداءً |
| Compare violation rates across business types | قارن معدلات المخالفات عبر أنواع الأنشطة |
| Year-over-year inspection comparison | مقارنة الفحوصات سنة بسنة |
| Which inspector has the best efficiency? | أي مفتش لديه أفضل كفاءة؟ |

#### Available Templates

| ID | Template Name (EN) | Template Name (AR) | Chart Type |
|----|-------------------|-------------------|------------|
| CMP_01 | Neighborhood Performance Comparison | مقارنة أداء الأحياء | Bar |
| CMP_02 | Year-over-Year Analysis | التحليل سنة بسنة | Line |
| CMP_03 | Inspector Performance Comparison | مقارنة أداء المفتشين | Bar |
| CMP_04 | Monthly Trend Comparison | مقارنة الاتجاهات الشهرية | Line |
| CMP_05 | Quarter Comparison | مقارنة الأرباع | Bar |
| CMP_06 | Violation Type Distribution | توزيع أنواع المخالفات | Pie |
| CMP_07 | First Half vs Second Half | النصف الأول مقابل النصف الثاني | Bar |
| CMP_08 | Top vs Bottom Locations | المواقع الأفضل مقابل الأسوأ | Bar |
| CMP_09 | Business Type Benchmarking | مقارنة أنواع الأنشطة | Bar |
| CMP_10 | Weekend vs Weekday Analysis | تحليل نهاية الأسبوع مقابل أيام العمل | Bar |
| CMP_11 | High-Volume vs Low-Volume Inspectors | المفتشون ذوو الحجم العالي مقابل المنخفض | Bar |
| CMP_12 | Compliance Score Brackets | شرائح درجات الامتثال | Pie |

---

### 4️⃣ Dimension 4: Predictive & Causal Analysis (11 Templates)

**Purpose:** Answer "Why?" questions and provide actionable recommendations

**What it does:**
- **Predictive:** Forecasts future trends based on historical patterns
- **Causal:** Identifies root causes of problems
- Provides actionable recommendations (not just data)
- Analyzes compliance trajectories (improving/declining/stable)
- Optimizes resource allocation (inspector workload balancing)

#### Recommendation Logic Example
```
Compliance Trajectory:
  If score_change > 10  → "Continue current approach"
  If score_change < -10 → "Needs intervention"
  Else                  → "Monitor closely"

Workload Optimization:
  If inspections > avg + σ → "Overloaded - Reduce assignments"
  If inspections < avg - σ → "Underutilized - Increase assignments"
  Else                     → "Optimal - Maintain current load"
```

#### Sample Questions

| English | العربية |
|---------|---------|
| Why are violations increasing in restaurants? | لماذا تزداد المخالفات في المطاعم؟ |
| Which locations are declining in compliance? | أي المواقع تتراجع في الامتثال؟ |
| What staffing do we need for summer season? | ما هو التوظيف الذي نحتاجه لموسم الصيف؟ |
| Predict violation trends for next quarter | توقع اتجاهات المخالفات للربع القادم |
| What are the root causes of repeat violations? | ما هي الأسباب الجذرية للمخالفات المتكررة؟ |
| Which locations need intervention? | أي المواقع تحتاج تدخل؟ |

#### Available Templates

| ID | Template Name (EN) | Template Name (AR) | Output Type |
|----|-------------------|-------------------|-------------|
| PRD_01 | High-Risk Location Prediction | توقع المواقع عالية المخاطر | Risk Level + Priority |
| PRD_02 | Violation Trend Prediction | توقع اتجاه المخالفات | Trend + Expected Rate |
| PRD_03 | Compliance Trajectory Analysis | تحليل مسار الامتثال | Trajectory + Recommendation |
| PRD_04 | Inspector Workload Optimization | تحسين حجم عمل المفتش | Status + Action |
| PRD_05 | Seasonal Risk Forecast | توقع المخاطر الموسمية | Forecast + Staffing Needs |
| PRD_06 | Root Cause Analysis | تحليل السبب الجذري | Cause + Recommended Action |
| PRD_07 | Recidivism Prediction | توقع التكرار | Probability + Risk Score |
| PRD_08 | Resource Allocation Optimization | تحسين تخصيص الموارد | Allocation Recommendation |
| PRD_09 | Early Warning System | نظام الإنذار المبكر | Warning Level + Action |
| PRD_10 | Improvement Opportunity Identification | تحديد فرص التحسين | Opportunity + Impact |
| PRD_11 | What-If Scenario Analysis | تحليل ماذا لو | Scenario Outcomes |

---

## Framework Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      4D ANALYSIS FRAMEWORK                          │
│                    (50 Specialized Templates)                       │
├─────────────────────┬───────────────────────────────────────────────┤
│                     │                                               │
│   DIMENSION 1       │  CORRELATION ANALYSIS                        │
│   📊 15 Templates   │  ─────────────────────                       │
│                     │  • What relates to what?                     │
│   "Relationships"   │  • Hidden patterns                           │
│                     │  • Multi-variable analysis                   │
│                     │                                               │
├─────────────────────┼───────────────────────────────────────────────┤
│                     │                                               │
│   DIMENSION 2       │  ANOMALY DETECTION                           │
│   🔍 12 Templates   │  ─────────────────────                       │
│                     │  • Statistical outliers (σ-based)            │
│   "Unusual"         │  • Suspicious patterns                       │
│                     │  • Performance extremes                      │
│                     │                                               │
├─────────────────────┼───────────────────────────────────────────────┤
│                     │                                               │
│   DIMENSION 3       │  COMPARATIVE ANALYSIS                        │
│   ⚖️ 12 Templates   │  ─────────────────────                       │
│                     │  • Benchmarking                              │
│   "Comparison"      │  • Time period analysis                      │
│                     │  • Best vs Worst rankings                    │
│                     │                                               │
├─────────────────────┼───────────────────────────────────────────────┤
│                     │                                               │
│   DIMENSION 4       │  PREDICTIVE & CAUSAL                         │
│   🎯 11 Templates   │  ─────────────────────                       │
│                     │  • Root cause identification                 │
│   "Why & What Next" │  • Trend forecasting                         │
│                     │  • Actionable recommendations                │
│                     │                                               │
└─────────────────────┴───────────────────────────────────────────────┘
```

---

## Key Differentiators

### From Data Retrieval → Intelligent Analysis

| Traditional Query | 4D Analysis |
|-------------------|-------------|
| "Show me violations" | "Why are violations increasing and what should we do?" |
| "List inspector counts" | "Which inspectors are overloaded and need workload rebalancing?" |
| "Monthly violation numbers" | "Detect unusual spikes and predict next month's trend" |
| "Top violation types" | "What are the root causes and how do we prevent them?" |

### Bilingual Support

All 50 templates support both Arabic (العربية) and English, with:
- Bilingual question examples
- RTL-compatible visualizations
- Arabic field names in results
- Culturally appropriate date/time formatting

### Actionable Outputs

Unlike simple data queries, 4D Analysis provides:
- **Classifications:** High Risk, Medium Risk, Low Risk
- **Trajectories:** Improving, Stable, Declining
- **Recommendations:** Specific actions to take
- **Predictions:** Expected values based on historical patterns

---

## Usage Examples

### Example 1: Correlation Query
**User:** "Is there a relationship between inspection duration and violations found?"

**System Response:**
- Scatter chart showing duration vs. violations
- Statistical correlation coefficient
- Insight: "Longer inspections (60+ min) find 2.3x more violations on average"

### Example 2: Anomaly Detection
**User:** "اكتشف المواقع ذات النشاط غير العادي" (Detect unusual locations)

**System Response:**
- List of locations flagged as "High Risk" or "Unusually Low"
- Statistical basis (> 2σ from mean)
- Bar chart highlighting anomalies in red

### Example 3: Comparative Analysis
**User:** "Compare Q1 vs Q2 performance"

**System Response:**
- Side-by-side metrics for both quarters
- Percentage change indicators
- Line chart showing trend progression

### Example 4: Predictive Analysis
**User:** "Which locations need intervention?"

**System Response:**
- Ranked list with compliance trajectory
- Classification: "Needs Intervention" / "Monitor" / "On Track"
- Specific recommendations per location

---

## Technical Implementation

The 4D Analysis Framework is implemented in:
- **File:** `/backend/nlp/sql_templates/analysis_4d.py`
- **Size:** 1,449 lines of specialized SQL templates
- **Integration:** Seamlessly integrated with the NLP query parser

### Intent Keywords

The system recognizes these intents to route to 4D templates:

| Dimension | Intent Keywords |
|-----------|-----------------|
| Correlation | CORRELATION, PATTERN, relationship, ارتباط |
| Anomaly | ANOMALY, SPIKE, unusual, outlier, شذوذ, غير عادي |
| Comparison | COMPARISON, compare, benchmark, مقارنة |
| Predictive | PREDICTIVE, CAUSAL, why, forecast, لماذا, توقع |

---

*Document Version: 1.0*  
*Last Updated: February 2026*  
*AlUla Inspection AI - Powered by Claude Sonnet 4.5*