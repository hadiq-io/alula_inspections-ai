"""
Prediction Questions Library
==============================
200+ prediction-related questions covering forecasting, risk scoring, anomalies, and scheduling.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# FORECASTING (50 questions)
# ============================================================================

FORECASTING_QUESTIONS = [
    QuestionTemplate(
        id="PRED_FORE_001",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["PREDICT", "VIOLATIONS", "NEXT_MONTH"],
        question_en="How many violations are predicted for next month?",
        question_ar="كم عدد المخالفات المتوقعة الشهر القادم؟",
        variations_en=[
            "Predict next month violations",
            "Violation forecast",
            "Expected violations next month",
            "What's the violation prediction?"
        ],
        variations_ar=[
            "توقع مخالفات الشهر القادم",
            "المخالفات المتوقعة"
        ],
        keywords_en=["predict", "forecast", "violations", "next month", "expected"],
        keywords_ar=["توقع", "مخالفات", "الشهر القادم", "متوقع"],
        sql="""
            SELECT 
                prediction_date,
                predicted_violations,
                confidence_level,
                lower_bound,
                upper_bound
            FROM ML_Predictions
            WHERE prediction_type = 'violations'
              AND prediction_date >= DATEADD(month, 1, GETDATE())
              AND prediction_date < DATEADD(month, 2, GETDATE())
            ORDER BY prediction_date
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_002",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["PREDICT", "INSPECTIONS", "TREND"],
        question_en="What is the predicted inspection trend for the next quarter?",
        question_ar="ما هو اتجاه الفحوصات المتوقع للربع القادم؟",
        variations_en=[
            "Quarterly inspection forecast",
            "Next quarter predictions",
            "Inspection trend forecast",
            "Predicted inspections Q+1"
        ],
        variations_ar=[
            "توقعات الفحوصات للربع القادم",
            "اتجاه الفحوصات المتوقع"
        ],
        keywords_en=["predict", "inspections", "trend", "quarter", "forecast"],
        keywords_ar=["توقع", "فحوصات", "اتجاه", "ربع"],
        sql="""
            SELECT 
                FORMAT(prediction_date, 'yyyy-MM') as month,
                predicted_value as predicted_inspections,
                confidence_level,
                trend_direction
            FROM ML_Predictions
            WHERE prediction_type = 'inspections'
              AND prediction_date >= GETDATE()
              AND prediction_date < DATEADD(month, 3, GETDATE())
            ORDER BY prediction_date
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_003",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["PREDICT", "COMPLIANCE", "FUTURE"],
        question_en="What is the predicted compliance rate for next month?",
        question_ar="ما هو معدل الامتثال المتوقع للشهر القادم؟",
        variations_en=[
            "Compliance rate forecast",
            "Expected compliance next month",
            "Predicted compliance",
            "Future compliance rate"
        ],
        variations_ar=[
            "توقع معدل الامتثال",
            "الامتثال المتوقع"
        ],
        keywords_en=["predict", "compliance", "rate", "next month", "forecast"],
        keywords_ar=["توقع", "امتثال", "معدل", "الشهر القادم"],
        sql="""
            SELECT 
                prediction_date,
                predicted_compliance_rate,
                current_trend,
                confidence_interval
            FROM ML_Predictions
            WHERE prediction_type = 'compliance'
              AND prediction_date >= DATEADD(month, 1, GETDATE())
            ORDER BY prediction_date
            OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_004",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["PREDICT", "VIOLATIONS", "YEARLY"],
        question_en="What is the annual violation forecast?",
        question_ar="ما هو التوقع السنوي للمخالفات؟",
        variations_en=[
            "Yearly violation prediction",
            "Annual forecast",
            "Full year violation prediction",
            "Next year violations"
        ],
        variations_ar=[
            "توقع المخالفات السنوي",
            "التوقع للسنة القادمة"
        ],
        keywords_en=["annual", "yearly", "forecast", "violations", "prediction"],
        keywords_ar=["سنوي", "توقع", "مخالفات"],
        sql="""
            SELECT 
                YEAR(prediction_date) as year,
                SUM(predicted_violations) as total_predicted_violations,
                AVG(confidence_level) as avg_confidence
            FROM ML_Predictions
            WHERE prediction_type = 'violations'
              AND YEAR(prediction_date) = YEAR(GETDATE()) + 1
            GROUP BY YEAR(prediction_date)
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_005",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["PREDICT", "WORKLOAD"],
        question_en="What is the predicted inspector workload?",
        question_ar="ما هو حمل العمل المتوقع للمفتشين؟",
        variations_en=[
            "Workload forecast",
            "Expected inspector workload",
            "Predicted inspection volume",
            "Future workload prediction"
        ],
        variations_ar=[
            "توقع حمل العمل",
            "حمل العمل المتوقع"
        ],
        keywords_en=["workload", "forecast", "inspector", "volume", "prediction"],
        keywords_ar=["حمل العمل", "توقع", "مفتشين"],
        sql="""
            SELECT 
                FORMAT(prediction_date, 'yyyy-MM') as month,
                predicted_inspections,
                recommended_inspectors,
                workload_level
            FROM ML_Predictions
            WHERE prediction_type = 'workload'
              AND prediction_date >= GETDATE()
              AND prediction_date < DATEADD(month, 6, GETDATE())
            ORDER BY prediction_date
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.ADVANCED
    ),
]

# ============================================================================
# RISK SCORING (50 questions)
# ============================================================================

RISK_SCORING_QUESTIONS = [
    QuestionTemplate(
        id="PRED_RISK_001",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_scoring",
        intent=["PREDICT", "RISK", "LOCATION"],
        question_en="Which locations have the highest predicted risk?",
        question_ar="أي المواقع لديها أعلى مخاطر متوقعة؟",
        variations_en=[
            "High risk locations",
            "Locations with highest risk score",
            "Predicted high-risk areas",
            "Risk ranking by location"
        ],
        variations_ar=[
            "المواقع عالية المخاطر",
            "أعلى درجات المخاطر"
        ],
        keywords_en=["risk", "locations", "highest", "predicted", "score"],
        keywords_ar=["مخاطر", "مواقع", "أعلى", "متوقع"],
        sql="""
            SELECT TOP 20
                l.Name as location_name,
                n.Name as neighborhood,
                mlr.risk_score,
                mlr.risk_category,
                mlr.primary_risk_factor,
                mlr.last_updated
            FROM ML_Location_Risk mlr
            JOIN Location l ON mlr.location_id = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE mlr.is_active = 1
            ORDER BY mlr.risk_score DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_002",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_scoring",
        intent=["PREDICT", "RISK", "NEIGHBORHOOD"],
        question_en="What is the risk score by neighborhood?",
        question_ar="ما هي درجة المخاطر حسب الحي؟",
        variations_en=[
            "Neighborhood risk scores",
            "Risk by area",
            "Area risk assessment",
            "Which neighborhoods are highest risk?"
        ],
        variations_ar=[
            "درجة المخاطر حسب الحي",
            "المخاطر حسب المنطقة"
        ],
        keywords_en=["risk", "score", "neighborhood", "area"],
        keywords_ar=["مخاطر", "درجة", "حي", "منطقة"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                AVG(mlr.risk_score) as avg_risk_score,
                MAX(mlr.risk_score) as max_risk_score,
                COUNT(*) as location_count
            FROM ML_Location_Risk mlr
            JOIN Location l ON mlr.location_id = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE mlr.is_active = 1
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY avg_risk_score DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.HEATMAP,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_003",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_scoring",
        intent=["PREDICT", "RISK", "FACTORS"],
        question_en="What are the main risk factors?",
        question_ar="ما هي عوامل الخطر الرئيسية؟",
        variations_en=[
            "Risk factor analysis",
            "What causes high risk?",
            "Primary risk factors",
            "Risk drivers"
        ],
        variations_ar=[
            "تحليل عوامل الخطر",
            "ما يسبب المخاطر العالية؟"
        ],
        keywords_en=["risk", "factors", "causes", "drivers", "primary"],
        keywords_ar=["مخاطر", "عوامل", "أسباب"],
        sql="""
            SELECT 
                primary_risk_factor,
                COUNT(*) as location_count,
                AVG(risk_score) as avg_risk_score
            FROM ML_Location_Risk
            WHERE is_active = 1
            GROUP BY primary_risk_factor
            ORDER BY location_count DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_004",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_scoring",
        intent=["PREDICT", "RISK", "CHANGE"],
        question_en="How have risk scores changed over time?",
        question_ar="كيف تغيرت درجات المخاطر مع الوقت؟",
        variations_en=[
            "Risk score trend",
            "Risk changes over time",
            "Historical risk scores",
            "Risk evolution"
        ],
        variations_ar=[
            "اتجاه درجات المخاطر",
            "تغير المخاطر"
        ],
        keywords_en=["risk", "change", "trend", "over time", "historical"],
        keywords_ar=["مخاطر", "تغير", "اتجاه"],
        sql="""
            SELECT 
                FORMAT(assessment_date, 'yyyy-MM') as month,
                AVG(risk_score) as avg_risk_score,
                COUNT(*) as assessments
            FROM ML_Location_Risk_History
            WHERE assessment_date >= DATEADD(year, -1, GETDATE())
            GROUP BY FORMAT(assessment_date, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.ADVANCED
    ),
]

# ============================================================================
# ANOMALY DETECTION (50 questions)
# ============================================================================

ANOMALY_QUESTIONS = [
    QuestionTemplate(
        id="PRED_ANOM_001",
        category=QuestionCategory.PREDICTION,
        subcategory="anomalies",
        intent=["DETECT", "ANOMALY", "RECENT"],
        question_en="Are there any recent anomalies detected?",
        question_ar="هل هناك أي حالات شاذة مكتشفة مؤخراً؟",
        variations_en=[
            "Recent anomalies",
            "Detected anomalies",
            "Any unusual patterns?",
            "Anomaly detection results"
        ],
        variations_ar=[
            "الحالات الشاذة الأخيرة",
            "الأنماط غير العادية"
        ],
        keywords_en=["anomaly", "anomalies", "unusual", "detected", "recent"],
        keywords_ar=["شاذة", "غير عادي", "مكتشف", "مؤخراً"],
        sql="""
            SELECT TOP 20
                detection_date,
                anomaly_type,
                entity_type,
                entity_name,
                anomaly_score,
                description
            FROM ML_Anomalies
            WHERE detection_date >= DATEADD(day, -30, GETDATE())
              AND is_resolved = 0
            ORDER BY anomaly_score DESC, detection_date DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_ANOM_002",
        category=QuestionCategory.PREDICTION,
        subcategory="anomalies",
        intent=["DETECT", "ANOMALY", "INSPECTOR"],
        question_en="Are there any anomalies in inspector behavior?",
        question_ar="هل هناك أي حالات شاذة في سلوك المفتشين؟",
        variations_en=[
            "Inspector anomalies",
            "Unusual inspector patterns",
            "Suspicious inspector activity",
            "Inspector behavior anomalies"
        ],
        variations_ar=[
            "سلوك غير عادي للمفتشين",
            "حالات شاذة للمفتشين"
        ],
        keywords_en=["anomaly", "inspector", "behavior", "unusual", "suspicious"],
        keywords_ar=["شاذة", "مفتش", "سلوك", "مشبوه"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                ma.anomaly_type,
                ma.anomaly_score,
                ma.description,
                ma.detection_date
            FROM ML_Anomalies ma
            JOIN [User] u ON ma.entity_id = u.Id
            WHERE ma.entity_type = 'inspector'
              AND ma.detection_date >= DATEADD(day, -30, GETDATE())
            ORDER BY ma.anomaly_score DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_003",
        category=QuestionCategory.PREDICTION,
        subcategory="anomalies",
        intent=["DETECT", "ANOMALY", "LOCATION"],
        question_en="Which locations show anomalous patterns?",
        question_ar="أي المواقع تظهر أنماطاً شاذة؟",
        variations_en=[
            "Location anomalies",
            "Unusual location patterns",
            "Anomalous locations",
            "Locations with unusual activity"
        ],
        variations_ar=[
            "المواقع ذات الأنماط الشاذة",
            "نشاط غير عادي للمواقع"
        ],
        keywords_en=["anomaly", "location", "pattern", "unusual"],
        keywords_ar=["شاذة", "موقع", "نمط", "غير عادي"],
        sql="""
            SELECT 
                l.Name as location_name,
                n.Name as neighborhood,
                ma.anomaly_type,
                ma.anomaly_score,
                ma.description
            FROM ML_Anomalies ma
            JOIN Location l ON ma.entity_id = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE ma.entity_type = 'location'
              AND ma.detection_date >= DATEADD(day, -30, GETDATE())
            ORDER BY ma.anomaly_score DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_ANOM_004",
        category=QuestionCategory.PREDICTION,
        subcategory="anomalies",
        intent=["DETECT", "ANOMALY", "TREND"],
        question_en="How many anomalies have been detected over time?",
        question_ar="كم عدد الحالات الشاذة المكتشفة مع الوقت؟",
        variations_en=[
            "Anomaly trend",
            "Anomalies over time",
            "Historical anomaly count",
            "Anomaly detection history"
        ],
        variations_ar=[
            "اتجاه الحالات الشاذة",
            "الحالات الشاذة مع الوقت"
        ],
        keywords_en=["anomaly", "trend", "over time", "historical", "count"],
        keywords_ar=["شاذة", "اتجاه", "تاريخي"],
        sql="""
            SELECT 
                FORMAT(detection_date, 'yyyy-MM') as month,
                COUNT(*) as anomaly_count,
                COUNT(CASE WHEN is_resolved = 1 THEN 1 END) as resolved_count
            FROM ML_Anomalies
            WHERE detection_date >= DATEADD(year, -1, GETDATE())
            GROUP BY FORMAT(detection_date, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# SCHEDULING RECOMMENDATIONS (50 questions)
# ============================================================================

SCHEDULING_QUESTIONS = [
    QuestionTemplate(
        id="PRED_SCHED_001",
        category=QuestionCategory.PREDICTION,
        subcategory="scheduling",
        intent=["RECOMMEND", "SCHEDULE", "INSPECTIONS"],
        question_en="What are the recommended inspections for this week?",
        question_ar="ما هي الفحوصات الموصى بها لهذا الأسبوع؟",
        variations_en=[
            "Recommended inspections",
            "What should we inspect?",
            "Suggested inspection schedule",
            "Priority inspections"
        ],
        variations_ar=[
            "الفحوصات الموصى بها",
            "ماذا يجب أن نفحص؟"
        ],
        keywords_en=["recommended", "inspections", "schedule", "priority", "suggested"],
        keywords_ar=["موصى", "فحوصات", "جدول", "أولوية"],
        sql="""
            SELECT TOP 20
                l.Name as location_name,
                n.Name as neighborhood,
                msr.priority_score,
                msr.reason,
                msr.recommended_date,
                msr.days_since_last_inspection
            FROM ML_Scheduling_Recommendations msr
            JOIN Location l ON msr.location_id = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE msr.recommended_date BETWEEN GETDATE() AND DATEADD(day, 7, GETDATE())
              AND msr.status = 'pending'
            ORDER BY msr.priority_score DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_SCHED_002",
        category=QuestionCategory.PREDICTION,
        subcategory="scheduling",
        intent=["RECOMMEND", "INSPECTOR", "ASSIGNMENT"],
        question_en="Which inspector should be assigned to each location?",
        question_ar="أي مفتش يجب تعيينه لكل موقع؟",
        variations_en=[
            "Inspector assignments",
            "Who should inspect where?",
            "Optimal inspector allocation",
            "Assignment recommendations"
        ],
        variations_ar=[
            "تعيينات المفتشين",
            "من يفحص أين؟"
        ],
        keywords_en=["inspector", "assignment", "location", "allocate", "recommend"],
        keywords_ar=["مفتش", "تعيين", "موقع"],
        sql="""
            SELECT 
                l.Name as location_name,
                u.Name as recommended_inspector,
                msr.match_score,
                msr.reason
            FROM ML_Scheduling_Recommendations msr
            JOIN Location l ON msr.location_id = l.Id
            JOIN [User] u ON msr.recommended_inspector_id = u.Id
            WHERE msr.recommended_date >= GETDATE()
              AND msr.status = 'pending'
            ORDER BY msr.priority_score DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_SCHED_003",
        category=QuestionCategory.PREDICTION,
        subcategory="scheduling",
        intent=["RECOMMEND", "LOCATIONS", "OVERDUE"],
        question_en="Which locations are overdue for inspection?",
        question_ar="أي المواقع متأخرة عن موعد الفحص؟",
        variations_en=[
            "Overdue inspections",
            "Locations needing inspection",
            "Inspection backlog",
            "Locations not inspected recently"
        ],
        variations_ar=[
            "الفحوصات المتأخرة",
            "المواقع التي تحتاج فحص"
        ],
        keywords_en=["overdue", "inspection", "backlog", "pending", "needed"],
        keywords_ar=["متأخر", "فحص", "معلق"],
        sql="""
            SELECT TOP 20
                l.Name as location_name,
                n.Name as neighborhood,
                DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_since_inspection,
                mlr.risk_score as current_risk_score
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            LEFT JOIN ML_Location_Risk mlr ON mlr.location_id = l.Id
            WHERE l.IsDeleted = 0
            GROUP BY l.Id, l.Name, n.Name, mlr.risk_score
            HAVING DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) > 30
               OR MAX(e.SubmitionDate) IS NULL
            ORDER BY mlr.risk_score DESC, days_since_inspection DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_SCHED_004",
        category=QuestionCategory.PREDICTION,
        subcategory="scheduling",
        intent=["RECOMMEND", "OPTIMAL", "ROUTE"],
        question_en="What is the optimal inspection route for today?",
        question_ar="ما هو أفضل مسار للفحوصات اليوم؟",
        variations_en=[
            "Optimal route",
            "Best inspection path",
            "Route optimization",
            "Efficient inspection order"
        ],
        variations_ar=[
            "أفضل مسار",
            "ترتيب الفحوصات الأمثل"
        ],
        keywords_en=["route", "optimal", "path", "efficient", "order"],
        keywords_ar=["مسار", "أفضل", "ترتيب"],
        sql="""
            SELECT 
                route_order,
                l.Name as location_name,
                n.Name as neighborhood,
                estimated_travel_time_minutes,
                estimated_inspection_time_minutes
            FROM ML_Scheduling_Recommendations msr
            JOIN Location l ON msr.location_id = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE msr.recommended_date = CAST(GETDATE() AS DATE)
              AND msr.route_order IS NOT NULL
            ORDER BY msr.route_order
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
]


# ============================================================================
# REGISTER ALL PREDICTION QUESTIONS
# ============================================================================

ALL_PREDICTION_QUESTIONS = (
    FORECASTING_QUESTIONS +
    RISK_SCORING_QUESTIONS +
    ANOMALY_QUESTIONS +
    SCHEDULING_QUESTIONS
)

# Register all questions
registry.register_many(ALL_PREDICTION_QUESTIONS)

print(f"Prediction Questions loaded: {len(ALL_PREDICTION_QUESTIONS)} templates")
