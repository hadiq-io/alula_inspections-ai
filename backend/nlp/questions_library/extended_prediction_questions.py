"""
Extended Prediction Questions Library
======================================
50+ additional prediction and forecasting questions covering machine learning,
anomaly detection, risk assessment, trend projection, and resource planning.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# FORECASTING QUESTIONS (10 questions)
# ============================================================================

FORECASTING_QUESTIONS = [
    QuestionTemplate(
        id="PRED_FORE_001",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "INSPECTIONS"],
        question_en="How many inspections will we need next month?",
        question_ar="كم عدد الفحوصات التي سنحتاجها الشهر القادم؟",
        variations_en=[
            "Next month inspection forecast",
            "Predicted inspections for next month",
            "Monthly inspection projection"
        ],
        variations_ar=["توقعات الفحوصات للشهر القادم", "عدد الفحوصات المتوقع"],
        keywords_en=["forecast", "next month", "predict", "inspections"],
        keywords_ar=["توقع", "الشهر القادم", "تنبؤ", "فحوصات"],
        sql="""
            SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                   COUNT(*) as inspections
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            ORDER BY month DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_002",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "VIOLATIONS"],
        question_en="What violations are likely to occur next quarter?",
        question_ar="ما المخالفات المحتملة في الربع القادم؟",
        variations_en=[
            "Predicted violations",
            "Expected violations next quarter",
            "Violation forecast"
        ],
        variations_ar=["المخالفات المتوقعة", "توقعات المخالفات"],
        keywords_en=["forecast", "violations", "next quarter", "likely"],
        keywords_ar=["توقع", "مخالفات", "الربع القادم", "محتمل"],
        sql="""
            SELECT vt.Name as violation_type,
                   DATEPART(QUARTER, e.SubmitionDate) as quarter,
                   COUNT(*) as occurrence_count
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name, DATEPART(QUARTER, e.SubmitionDate)
            ORDER BY vt.Name, quarter
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_FORE_003",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "COMPLIANCE"],
        question_en="What will be our compliance rate next quarter?",
        question_ar="ما سيكون معدل الامتثال في الربع القادم؟",
        variations_en=[
            "Predicted compliance rate",
            "Compliance forecast",
            "Expected compliance"
        ],
        variations_ar=["معدل الامتثال المتوقع", "توقعات الامتثال"],
        keywords_en=["forecast", "compliance", "next quarter", "predict"],
        keywords_ar=["توقع", "امتثال", "الربع القادم"],
        sql="""
            SELECT CONCAT('Q', DATEPART(QUARTER, SubmitionDate)) as quarter,
                   CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY DATEPART(QUARTER, SubmitionDate)
            ORDER BY DATEPART(QUARTER, SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_004",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "RESOURCES"],
        question_en="How many inspectors will we need next month?",
        question_ar="كم عدد المفتشين الذين سنحتاجهم الشهر القادم؟",
        variations_en=[
            "Inspector capacity forecast",
            "Resource requirements prediction",
            "Staffing needs projection"
        ],
        variations_ar=["توقعات طاقة المفتشين", "تنبؤ متطلبات الموارد"],
        keywords_en=["forecast", "inspectors", "resources", "capacity"],
        keywords_ar=["توقع", "مفتشين", "موارد", "طاقة"],
        sql="""
            SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                   COUNT(DISTINCT ReporterID) as active_inspectors,
                   COUNT(*) as total_inspections,
                   CAST(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT ReporterID), 0) AS DECIMAL(5,2)) as inspections_per_inspector
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            ORDER BY month DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_005",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "WORKLOAD"],
        question_en="What is the projected workload for next week?",
        question_ar="ما هو حمل العمل المتوقع للأسبوع القادم؟",
        variations_en=[
            "Weekly workload projection",
            "Next week forecast",
            "Predicted workload"
        ],
        variations_ar=["توقعات حمل العمل الأسبوعي", "تنبؤ الأسبوع القادم"],
        keywords_en=["forecast", "workload", "next week", "projection"],
        keywords_ar=["توقع", "حمل عمل", "الأسبوع القادم"],
        sql="""
            SELECT DATEPART(WEEK, SubmitionDate) as week_number,
                   COUNT(*) as inspections
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY DATEPART(WEEK, SubmitionDate)
            ORDER BY week_number DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="PRED_FORE_006",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "TREND"],
        question_en="What is the projected score trend for the year?",
        question_ar="ما هو اتجاه الدرجات المتوقع للسنة؟",
        variations_en=[
            "Score trend projection",
            "Yearly score forecast",
            "Expected score trajectory"
        ],
        variations_ar=["توقعات اتجاه الدرجات", "تنبؤ الدرجات السنوي"],
        keywords_en=["trend", "projected", "score", "year"],
        keywords_ar=["اتجاه", "متوقع", "درجة", "سنة"],
        sql="""
            SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                   CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="PRED_FORE_007",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "SEASONAL"],
        question_en="What seasonal patterns should we expect?",
        question_ar="ما الأنماط الموسمية التي يجب توقعها؟",
        variations_en=[
            "Seasonal forecast",
            "Seasonal patterns",
            "Expected seasonal trends"
        ],
        variations_ar=["التوقعات الموسمية", "الأنماط الموسمية"],
        keywords_en=["seasonal", "patterns", "expect", "forecast"],
        keywords_ar=["موسمي", "أنماط", "توقع"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(*) as inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(SubmitionDate) IN (12, 1, 2) THEN 'Winter' WHEN MONTH(SubmitionDate) IN (3, 4, 5) THEN 'Spring' WHEN MONTH(SubmitionDate) IN (6, 7, 8) THEN 'Summer' ELSE 'Fall' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_008",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "BUDGET"],
        question_en="What is the projected violation cost for next quarter?",
        question_ar="ما هي تكلفة المخالفات المتوقعة للربع القادم؟",
        variations_en=[
            "Violation cost forecast",
            "Projected penalties",
            "Expected violation costs"
        ],
        variations_ar=["توقعات تكلفة المخالفات", "الغرامات المتوقعة"],
        keywords_en=["forecast", "cost", "budget", "projected"],
        keywords_ar=["توقع", "تكلفة", "ميزانية"],
        sql="""
            SELECT CONCAT('Q', DATEPART(QUARTER, e.SubmitionDate)) as quarter,
                   SUM(ev.Value) as total_violation_value,
                   COUNT(ev.Id) as violation_count
            FROM Event e
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(QUARTER, e.SubmitionDate)
            ORDER BY DATEPART(QUARTER, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_FORE_009",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "GROWTH"],
        question_en="What is the projected inspection volume growth?",
        question_ar="ما هو نمو حجم الفحوصات المتوقع؟",
        variations_en=[
            "Volume growth forecast",
            "Inspection growth rate",
            "Expected volume increase"
        ],
        variations_ar=["توقعات نمو الحجم", "معدل نمو الفحوصات"],
        keywords_en=["growth", "volume", "increase", "projected"],
        keywords_ar=["نمو", "حجم", "زيادة", "متوقع"],
        sql="""
            WITH MonthlyVolume AS (
                SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                       COUNT(*) as volume
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
                GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            )
            SELECT m1.month, m1.volume,
                   CAST((m1.volume - m2.volume) * 100.0 / NULLIF(m2.volume, 0) AS DECIMAL(5,2)) as growth_pct
            FROM MonthlyVolume m1
            LEFT JOIN MonthlyVolume m2 ON m2.month = FORMAT(DATEADD(MONTH, -1, CAST(m1.month + '-01' AS DATE)), 'yyyy-MM')
            ORDER BY m1.month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_FORE_010",
        category=QuestionCategory.PREDICTION,
        subcategory="forecasting",
        intent=["FORECAST", "YEAR_END"],
        question_en="What will be our year-end performance?",
        question_ar="ما سيكون أداؤنا في نهاية العام؟",
        variations_en=[
            "Year-end forecast",
            "End of year projection",
            "Annual performance prediction"
        ],
        variations_ar=["توقعات نهاية العام", "تنبؤ الأداء السنوي"],
        keywords_en=["year-end", "forecast", "annual", "projection"],
        keywords_ar=["نهاية العام", "توقع", "سنوي"],
        sql="""
            SELECT 
                COUNT(*) as ytd_inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as ytd_avg_score,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as ytd_compliance,
                CAST(COUNT(*) * 12.0 / MONTH(GETDATE()) AS INT) as projected_annual_inspections
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# RISK PREDICTION QUESTIONS (10 questions)
# ============================================================================

RISK_PREDICTION_QUESTIONS = [
    QuestionTemplate(
        id="PRED_RISK_001",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "HIGH_RISK"],
        question_en="Which locations are likely to fail their next inspection?",
        question_ar="أي المواقع من المحتمل أن تفشل في الفحص القادم؟",
        variations_en=[
            "Predicted failures",
            "At-risk locations",
            "Locations likely to fail"
        ],
        variations_ar=["الفشل المتوقع", "المواقع المعرضة للخطر"],
        keywords_en=["predict", "fail", "likely", "at-risk"],
        keywords_ar=["تنبؤ", "فشل", "محتمل", "خطر"],
        sql="""
            SELECT l.Name as location,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(e.Id) as inspections,
                   COUNT(CASE WHEN e.Score < 80 THEN 1 END) as failed_inspections,
                   CAST(COUNT(CASE WHEN e.Score < 80 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as failure_rate
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING AVG(e.Score) < 75
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_002",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "VIOLATIONS", "TYPE"],
        question_en="What types of violations are most likely to occur?",
        question_ar="ما أنواع المخالفات الأكثر احتمالاً للحدوث؟",
        variations_en=[
            "Likely violations",
            "Expected violation types",
            "Predicted violation categories"
        ],
        variations_ar=["المخالفات المحتملة", "أنواع المخالفات المتوقعة"],
        keywords_en=["likely", "violations", "types", "occur"],
        keywords_ar=["محتمل", "مخالفات", "أنواع", "حدوث"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(*) as historical_count,
                   CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS DECIMAL(5,2)) as probability_pct
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            ORDER BY historical_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_003",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "RISK", "SCORE"],
        question_en="What is the predicted risk score for each neighborhood?",
        question_ar="ما هي درجة المخاطر المتوقعة لكل حي؟",
        variations_en=[
            "Neighborhood risk scores",
            "Predicted risk by area",
            "Risk assessment by zone"
        ],
        variations_ar=["درجات مخاطر الأحياء", "المخاطر المتوقعة بالمنطقة"],
        keywords_en=["risk", "score", "neighborhood", "predicted"],
        keywords_ar=["مخاطر", "درجة", "حي", "متوقع"],
        sql="""
            SELECT n.Name as neighborhood,
                   100 - CAST(AVG(e.Score) AS DECIMAL(5,2)) as risk_score,
                   COUNT(ev.Id) as violation_count,
                   CASE 
                       WHEN AVG(e.Score) < 60 THEN 'High Risk'
                       WHEN AVG(e.Score) < 80 THEN 'Medium Risk'
                       ELSE 'Low Risk'
                   END as risk_level
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY risk_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_004",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "DECLINE"],
        question_en="Which locations are showing declining performance?",
        question_ar="أي المواقع تظهر تراجعاً في الأداء؟",
        variations_en=[
            "Declining locations",
            "Performance decline prediction",
            "Locations getting worse"
        ],
        variations_ar=["المواقع المتراجعة", "تنبؤ تراجع الأداء"],
        keywords_en=["declining", "worse", "decreasing", "performance"],
        keywords_ar=["تراجع", "أسوأ", "انخفاض", "أداء"],
        sql="""
            WITH RecentScores AS (
                SELECT e.LocationID, e.Score, e.SubmitionDate,
                       ROW_NUMBER() OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate DESC) as rn
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT l.Name as location,
                   recent.Score as latest_score,
                   prev.Score as previous_score,
                   recent.Score - prev.Score as score_change
            FROM Location l
            JOIN RecentScores recent ON recent.LocationID = l.Id AND recent.rn = 1
            JOIN RecentScores prev ON prev.LocationID = l.Id AND prev.rn = 2
            WHERE recent.Score < prev.Score
            ORDER BY score_change ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_RISK_005",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "CRITICAL"],
        question_en="Where are critical violations most likely to occur?",
        question_ar="أين من المحتمل أن تحدث المخالفات الحرجة؟",
        variations_en=[
            "Critical violation prediction",
            "High severity risk areas",
            "Where will critical issues occur?"
        ],
        variations_ar=["تنبؤ المخالفات الحرجة", "مناطق الخطر العالي"],
        keywords_en=["critical", "likely", "occur", "severe"],
        keywords_ar=["حرج", "محتمل", "حدوث", "شديد"],
        sql="""
            SELECT l.Name as location,
                   COUNT(CASE WHEN e.Score < 50 THEN 1 END) as critical_events,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(CASE WHEN e.Score < 50 THEN 1 END) > 0
            ORDER BY critical_events DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_006",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "REPEAT", "OFFENDER"],
        question_en="Which locations are likely to be repeat offenders?",
        question_ar="أي المواقع من المحتمل أن تكون مخالفة متكررة؟",
        variations_en=[
            "Repeat offender prediction",
            "Likely recurring violations",
            "Predicted repeat failures"
        ],
        variations_ar=["تنبؤ المخالفين المتكررين", "المخالفات المتكررة المحتملة"],
        keywords_en=["repeat", "offender", "recurring", "likely"],
        keywords_ar=["متكرر", "مخالف", "محتمل"],
        sql="""
            SELECT l.Name as location,
                   COUNT(ev.Id) as total_violations,
                   COUNT(DISTINCT e.Id) as events_with_violations,
                   CAST(COUNT(ev.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.Id), 0) AS DECIMAL(5,2)) as violations_per_event
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(ev.Id) > 3
            ORDER BY violations_per_event DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_RISK_007",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "ESCALATION"],
        question_en="Which issues are likely to escalate?",
        question_ar="أي المشاكل من المحتمل أن تتصاعد؟",
        variations_en=[
            "Escalation prediction",
            "Issues likely to get worse",
            "Predicted escalations"
        ],
        variations_ar=["تنبؤ التصاعد", "المشاكل المحتمل تفاقمها"],
        keywords_en=["escalate", "worse", "increase", "predict"],
        keywords_ar=["تصاعد", "أسوأ", "زيادة", "تنبؤ"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN 1 END) as h1_count,
                   COUNT(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN 1 END) as h2_count,
                   COUNT(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN 1 END) - COUNT(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN 1 END) as increase
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            HAVING COUNT(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN 1 END) > COUNT(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN 1 END)
            ORDER BY increase DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_RISK_008",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "OVERDUE"],
        question_en="Which locations are likely to become overdue for inspection?",
        question_ar="أي المواقع من المحتمل أن تتأخر في الفحص؟",
        variations_en=[
            "Overdue inspection prediction",
            "Locations needing inspection soon",
            "Predicted overdue sites"
        ],
        variations_ar=["تنبؤ تأخر الفحص", "المواقع التي تحتاج فحص قريباً"],
        keywords_en=["overdue", "soon", "inspection", "predict"],
        keywords_ar=["متأخر", "قريباً", "فحص", "تنبؤ"],
        sql="""
            SELECT l.Name as location,
                   MAX(e.SubmitionDate) as last_inspection,
                   DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_since_inspection
            FROM Location l
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            GROUP BY l.Id, l.Name
            HAVING DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) > 30 OR MAX(e.SubmitionDate) IS NULL
            ORDER BY days_since_inspection DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RISK_009",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "SEASONAL", "RISK"],
        question_en="What seasonal risks should we prepare for?",
        question_ar="ما المخاطر الموسمية التي يجب الاستعداد لها؟",
        variations_en=[
            "Seasonal risk prediction",
            "Upcoming seasonal challenges",
            "Expected seasonal issues"
        ],
        variations_ar=["تنبؤ المخاطر الموسمية", "التحديات الموسمية القادمة"],
        keywords_en=["seasonal", "risk", "prepare", "predict"],
        keywords_ar=["موسمي", "مخاطر", "استعداد", "تنبؤ"],
        sql="""
            SELECT vt.Name as violation_type,
                   CASE 
                       WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                       WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                       WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                       ELSE 'Fall'
                   END as season,
                   COUNT(*) as occurrence_count
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) >= {year} - 1
            GROUP BY vt.Id, vt.Name, 
                     CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter' WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring' WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer' ELSE 'Fall' END
            ORDER BY season, occurrence_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_RISK_010",
        category=QuestionCategory.PREDICTION,
        subcategory="risk_prediction",
        intent=["PREDICT", "COMPLIANCE", "RISK"],
        question_en="What is the predicted compliance risk for each category?",
        question_ar="ما هي مخاطر الامتثال المتوقعة لكل فئة؟",
        variations_en=[
            "Category compliance risk",
            "Predicted category risks",
            "Risk by violation category"
        ],
        variations_ar=["مخاطر امتثال الفئات", "المخاطر المتوقعة بالفئة"],
        keywords_en=["compliance", "risk", "category", "predicted"],
        keywords_ar=["امتثال", "مخاطر", "فئة", "متوقع"],
        sql="""
            SELECT vc.Name as category,
                   COUNT(ev.Id) as violation_count,
                   CAST(COUNT(ev.Id) * 100.0 / SUM(COUNT(ev.Id)) OVER () AS DECIMAL(5,2)) as risk_share_pct
            FROM ViolationCategory vc
            JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY violation_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# ANOMALY DETECTION QUESTIONS (10 questions)
# ============================================================================

ANOMALY_DETECTION_QUESTIONS = [
    QuestionTemplate(
        id="PRED_ANOM_001",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "SCORES"],
        question_en="Are there any anomalous inspection scores?",
        question_ar="هل هناك أي درجات فحص شاذة؟",
        variations_en=[
            "Unusual scores",
            "Outlier scores",
            "Abnormal inspection results"
        ],
        variations_ar=["درجات غير عادية", "قيم شاذة"],
        keywords_en=["anomaly", "unusual", "outlier", "abnormal"],
        keywords_ar=["شاذ", "غير عادي", "غريب"],
        sql="""
            WITH Stats AS (
                SELECT AVG(Score) as avg_score, STDEV(Score) as std_dev
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            )
            SELECT e.Id, l.Name as location, e.Score,
                   CAST((e.Score - s.avg_score) / NULLIF(s.std_dev, 0) AS DECIMAL(5,2)) as z_score
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            CROSS JOIN Stats s
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            AND ABS(e.Score - s.avg_score) > 2 * s.std_dev
            ORDER BY ABS(e.Score - s.avg_score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_002",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "VOLUME"],
        question_en="Are there any days with unusual inspection volume?",
        question_ar="هل هناك أيام بحجم فحوصات غير عادي؟",
        variations_en=[
            "Unusual inspection days",
            "Volume anomalies",
            "Abnormal activity days"
        ],
        variations_ar=["أيام فحوصات غير عادية", "شذوذ في الحجم"],
        keywords_en=["unusual", "volume", "days", "anomaly"],
        keywords_ar=["غير عادي", "حجم", "أيام", "شذوذ"],
        sql="""
            WITH DailyStats AS (
                SELECT CAST(SubmitionDate AS DATE) as date, COUNT(*) as daily_count
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
                GROUP BY CAST(SubmitionDate AS DATE)
            ),
            OverallStats AS (
                SELECT AVG(daily_count) as avg_count, STDEV(daily_count) as std_dev FROM DailyStats
            )
            SELECT d.date, d.daily_count,
                   CAST((d.daily_count - o.avg_count) / NULLIF(o.std_dev, 0) AS DECIMAL(5,2)) as z_score
            FROM DailyStats d
            CROSS JOIN OverallStats o
            WHERE ABS(d.daily_count - o.avg_count) > 2 * o.std_dev
            ORDER BY d.date DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_003",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "INSPECTOR"],
        question_en="Are any inspectors showing unusual patterns?",
        question_ar="هل أي مفتش يظهر أنماطاً غير عادية؟",
        variations_en=[
            "Inspector anomalies",
            "Unusual inspector behavior",
            "Inspector pattern anomalies"
        ],
        variations_ar=["شذوذ المفتشين", "سلوك مفتش غير عادي"],
        keywords_en=["inspector", "unusual", "pattern", "anomaly"],
        keywords_ar=["مفتش", "غير عادي", "نمط", "شذوذ"],
        sql="""
            WITH InspectorStats AS (
                SELECT u.Id, u.Name,
                       AVG(e.Score) as avg_score,
                       STDEV(e.Score) as score_std,
                       COUNT(e.Id) as count
                FROM [User] u
                JOIN Event e ON e.ReporterID = u.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY u.Id, u.Name
            ),
            OverallStats AS (
                SELECT AVG(avg_score) as mean_avg, STDEV(avg_score) as std_avg FROM InspectorStats WHERE count >= 5
            )
            SELECT i.Name as inspector, i.count as inspections,
                   CAST(i.avg_score AS DECIMAL(5,2)) as avg_score,
                   CAST(i.score_std AS DECIMAL(5,2)) as score_variation
            FROM InspectorStats i
            CROSS JOIN OverallStats o
            WHERE i.count >= 5 AND (i.score_std > 15 OR ABS(i.avg_score - o.mean_avg) > 2 * o.std_avg)
            ORDER BY i.score_std DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_004",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "SUDDEN", "CHANGE"],
        question_en="Are there any sudden score changes at locations?",
        question_ar="هل هناك تغييرات مفاجئة في درجات المواقع؟",
        variations_en=[
            "Sudden score changes",
            "Abrupt performance changes",
            "Unexpected score shifts"
        ],
        variations_ar=["تغييرات مفاجئة في الدرجات", "تحولات غير متوقعة"],
        keywords_en=["sudden", "change", "abrupt", "unexpected"],
        keywords_ar=["مفاجئ", "تغيير", "حاد", "غير متوقع"],
        sql="""
            WITH ScoreChanges AS (
                SELECT e.LocationID, e.Score, e.SubmitionDate,
                       LAG(e.Score) OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as prev_score
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT l.Name as location, s.Score as current_score, s.prev_score,
                   s.Score - s.prev_score as change
            FROM ScoreChanges s
            JOIN Location l ON s.LocationID = l.Id
            WHERE ABS(s.Score - s.prev_score) > 20 AND s.prev_score IS NOT NULL
            ORDER BY ABS(s.Score - s.prev_score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_005",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "VIOLATION", "SPIKE"],
        question_en="Are there any violation spikes?",
        question_ar="هل هناك أي طفرات في المخالفات؟",
        variations_en=[
            "Violation spikes",
            "Sudden violation increases",
            "Violation surge detection"
        ],
        variations_ar=["طفرات المخالفات", "زيادات مفاجئة في المخالفات"],
        keywords_en=["spike", "surge", "increase", "violation"],
        keywords_ar=["طفرة", "زيادة", "مخالفات"],
        sql="""
            WITH WeeklyViolations AS (
                SELECT DATEPART(WEEK, e.SubmitionDate) as week_num,
                       COUNT(ev.Id) as violations
                FROM Event e
                LEFT JOIN EventViolation ev ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY DATEPART(WEEK, e.SubmitionDate)
            ),
            Stats AS (
                SELECT AVG(violations) as avg_violations, STDEV(violations) as std_violations FROM WeeklyViolations
            )
            SELECT w.week_num, w.violations,
                   CAST((w.violations - s.avg_violations) / NULLIF(s.std_violations, 0) AS DECIMAL(5,2)) as z_score
            FROM WeeklyViolations w
            CROSS JOIN Stats s
            WHERE w.violations > s.avg_violations + 2 * s.std_violations
            ORDER BY w.violations DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_006",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "LOCATION", "BEHAVIOR"],
        question_en="Which locations have anomalous behavior patterns?",
        question_ar="أي المواقع لديها أنماط سلوك شاذة؟",
        variations_en=[
            "Location anomalies",
            "Unusual location patterns",
            "Abnormal location behavior"
        ],
        variations_ar=["شذوذ المواقع", "أنماط مواقع غير عادية"],
        keywords_en=["location", "anomaly", "behavior", "pattern"],
        keywords_ar=["موقع", "شذوذ", "سلوك", "نمط"],
        sql="""
            WITH LocationStats AS (
                SELECT l.Id, l.Name, AVG(e.Score) as avg_score, STDEV(e.Score) as score_std, COUNT(e.Id) as count
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id, l.Name
                HAVING COUNT(e.Id) >= 3
            )
            SELECT Name as location, count as inspections,
                   CAST(avg_score AS DECIMAL(5,2)) as avg_score,
                   CAST(score_std AS DECIMAL(5,2)) as score_variation
            FROM LocationStats
            WHERE score_std > 15
            ORDER BY score_std DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_007",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "TIME", "GAP"],
        question_en="Are there unusual gaps in inspection schedules?",
        question_ar="هل هناك فجوات غير عادية في جداول الفحص؟",
        variations_en=[
            "Schedule gaps",
            "Inspection gaps",
            "Missing inspection periods"
        ],
        variations_ar=["فجوات الجدول", "فجوات الفحص"],
        keywords_en=["gap", "schedule", "missing", "unusual"],
        keywords_ar=["فجوة", "جدول", "مفقود", "غير عادي"],
        sql="""
            WITH InspectionGaps AS (
                SELECT l.Id, l.Name,
                       e.SubmitionDate,
                       LEAD(e.SubmitionDate) OVER (PARTITION BY l.Id ORDER BY e.SubmitionDate) as next_inspection,
                       DATEDIFF(day, e.SubmitionDate, LEAD(e.SubmitionDate) OVER (PARTITION BY l.Id ORDER BY e.SubmitionDate)) as gap_days
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT Name as location, gap_days,
                   FORMAT(SubmitionDate, 'yyyy-MM-dd') as from_date,
                   FORMAT(next_inspection, 'yyyy-MM-dd') as to_date
            FROM InspectionGaps
            WHERE gap_days > 60
            ORDER BY gap_days DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_ANOM_008",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "CATEGORY", "UNUSUAL"],
        question_en="Are there unusual patterns in violation categories?",
        question_ar="هل هناك أنماط غير عادية في فئات المخالفات؟",
        variations_en=[
            "Category anomalies",
            "Unusual category patterns",
            "Category distribution anomalies"
        ],
        variations_ar=["شذوذ الفئات", "أنماط فئات غير عادية"],
        keywords_en=["category", "unusual", "pattern", "anomaly"],
        keywords_ar=["فئة", "غير عادي", "نمط", "شذوذ"],
        sql="""
            WITH CategoryMonthly AS (
                SELECT vc.Name as category, FORMAT(e.SubmitionDate, 'yyyy-MM') as month, COUNT(*) as count
                FROM ViolationCategory vc
                JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
                JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
                JOIN Event e ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY vc.Id, vc.Name, FORMAT(e.SubmitionDate, 'yyyy-MM')
            )
            SELECT category, month, count
            FROM CategoryMonthly
            WHERE count > (SELECT AVG(count) + 2 * STDEV(count) FROM CategoryMonthly)
            ORDER BY count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_ANOM_009",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "PERFECT", "SCORES"],
        question_en="Are there suspiciously perfect scores?",
        question_ar="هل هناك درجات مثالية مشبوهة؟",
        variations_en=[
            "Perfect score anomalies",
            "Suspiciously high scores",
            "Too-good scores"
        ],
        variations_ar=["درجات مثالية مشبوهة", "درجات مرتفعة جداً"],
        keywords_en=["perfect", "suspicious", "too good", "100"],
        keywords_ar=["مثالي", "مشبوه", "ممتاز جداً"],
        sql="""
            SELECT l.Name as location, u.Name as inspector,
                   COUNT(*) as perfect_count
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND e.Score = 100 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name, u.Id, u.Name
            HAVING COUNT(*) >= 3
            ORDER BY perfect_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_ANOM_010",
        category=QuestionCategory.PREDICTION,
        subcategory="anomaly_detection",
        intent=["ANOMALY", "NEIGHBORHOOD", "OUTLIER"],
        question_en="Which neighborhoods are statistical outliers?",
        question_ar="أي الأحياء هي قيم متطرفة إحصائياً؟",
        variations_en=[
            "Neighborhood outliers",
            "Statistical outlier areas",
            "Extreme neighborhoods"
        ],
        variations_ar=["أحياء متطرفة", "مناطق شاذة إحصائياً"],
        keywords_en=["neighborhood", "outlier", "statistical", "extreme"],
        keywords_ar=["حي", "متطرف", "إحصائي", "شاذ"],
        sql="""
            WITH NeighborhoodStats AS (
                SELECT n.Id, n.Name, AVG(e.Score) as avg_score
                FROM Neighborhood n
                JOIN Location l ON l.NeighborhoodID = n.Id
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY n.Id, n.Name
            ),
            OverallStats AS (
                SELECT AVG(avg_score) as mean_score, STDEV(avg_score) as std_score FROM NeighborhoodStats
            )
            SELECT ns.Name as neighborhood,
                   CAST(ns.avg_score AS DECIMAL(5,2)) as avg_score,
                   CAST((ns.avg_score - o.mean_score) / NULLIF(o.std_score, 0) AS DECIMAL(5,2)) as z_score
            FROM NeighborhoodStats ns
            CROSS JOIN OverallStats o
            WHERE ABS(ns.avg_score - o.mean_score) > 1.5 * o.std_score
            ORDER BY ABS(ns.avg_score - o.mean_score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
]

# ============================================================================
# RESOURCE PLANNING QUESTIONS (10 questions)
# ============================================================================

RESOURCE_PLANNING_QUESTIONS = [
    QuestionTemplate(
        id="PRED_RES_001",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "ALLOCATION"],
        question_en="How should we allocate inspectors next month?",
        question_ar="كيف يجب توزيع المفتشين الشهر القادم؟",
        variations_en=[
            "Inspector allocation plan",
            "Resource distribution",
            "Staff allocation"
        ],
        variations_ar=["خطة توزيع المفتشين", "توزيع الموارد"],
        keywords_en=["allocate", "inspector", "resource", "plan"],
        keywords_ar=["توزيع", "مفتش", "موارد", "خطة"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(DISTINCT l.Id) as locations,
                   CAST(COUNT(DISTINCT l.Id) * 1.0 / NULLIF(SUM(COUNT(DISTINCT l.Id)) OVER (), 0) * 100 AS DECIMAL(5,2)) as allocation_pct
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            WHERE l.IsDeleted = 0
            GROUP BY n.Id, n.Name
            ORDER BY locations DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_002",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "CAPACITY"],
        question_en="Do we have enough inspector capacity?",
        question_ar="هل لدينا طاقة كافية من المفتشين؟",
        variations_en=[
            "Inspector capacity analysis",
            "Capacity assessment",
            "Staff sufficiency"
        ],
        variations_ar=["تحليل طاقة المفتشين", "تقييم القدرة"],
        keywords_en=["capacity", "enough", "staff", "sufficient"],
        keywords_ar=["طاقة", "كافي", "موظفين"],
        sql="""
            SELECT 
                COUNT(DISTINCT e.ReporterID) as active_inspectors,
                COUNT(e.Id) as total_inspections,
                COUNT(DISTINCT l.Id) as total_locations,
                CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.ReporterID), 0) AS DECIMAL(5,2)) as inspections_per_inspector,
                CAST(COUNT(DISTINCT l.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.ReporterID), 0) AS DECIMAL(5,2)) as locations_per_inspector
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_003",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "PRIORITY"],
        question_en="Which areas should be prioritized for inspection?",
        question_ar="أي المناطق يجب إعطاؤها الأولوية للفحص؟",
        variations_en=[
            "Priority areas",
            "Where to focus inspections",
            "Inspection priorities"
        ],
        variations_ar=["المناطق ذات الأولوية", "أين نركز الفحوصات"],
        keywords_en=["priority", "focus", "areas", "prioritize"],
        keywords_ar=["أولوية", "تركيز", "مناطق"],
        sql="""
            SELECT n.Name as neighborhood,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_since_inspection,
                   CASE 
                       WHEN AVG(e.Score) < 70 OR DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) > 30 THEN 'High'
                       WHEN AVG(e.Score) < 80 THEN 'Medium'
                       ELSE 'Low'
                   END as priority
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_004",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "SCHEDULE"],
        question_en="What should be the inspection schedule for next week?",
        question_ar="ما يجب أن يكون جدول الفحوصات للأسبوع القادم؟",
        variations_en=[
            "Inspection schedule",
            "Next week plan",
            "Weekly schedule"
        ],
        variations_ar=["جدول الفحوصات", "خطة الأسبوع القادم"],
        keywords_en=["schedule", "next week", "plan", "calendar"],
        keywords_ar=["جدول", "الأسبوع القادم", "خطة"],
        sql="""
            SELECT l.Name as location,
                   MAX(e.SubmitionDate) as last_inspection,
                   DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_since,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Location l
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            WHERE l.IsDeleted = 0
            GROUP BY l.Id, l.Name
            HAVING DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) > 14 OR MAX(e.SubmitionDate) IS NULL
            ORDER BY days_since DESC, avg_score ASC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_005",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "TRAINING"],
        question_en="Which inspectors need additional training?",
        question_ar="أي المفتشين يحتاجون تدريباً إضافياً؟",
        variations_en=[
            "Training needs",
            "Inspector skill gaps",
            "Who needs training?"
        ],
        variations_ar=["احتياجات التدريب", "فجوات مهارات المفتشين"],
        keywords_en=["training", "need", "skill", "improvement"],
        keywords_ar=["تدريب", "حاجة", "مهارة", "تحسين"],
        sql="""
            WITH InspectorPerformance AS (
                SELECT u.Id, u.Name, AVG(e.Score) as avg_score, STDEV(e.Score) as score_variation, COUNT(e.Id) as count
                FROM [User] u
                JOIN Event e ON e.ReporterID = u.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY u.Id, u.Name
                HAVING COUNT(e.Id) >= 5
            ),
            OverallStats AS (
                SELECT AVG(avg_score) as mean_score FROM InspectorPerformance
            )
            SELECT i.Name as inspector, i.count as inspections,
                   CAST(i.avg_score AS DECIMAL(5,2)) as avg_score,
                   CAST(i.score_variation AS DECIMAL(5,2)) as consistency
            FROM InspectorPerformance i
            CROSS JOIN OverallStats o
            WHERE i.avg_score < o.mean_score - 5 OR i.score_variation > 15
            ORDER BY i.avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_006",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "WORKLOAD", "BALANCE"],
        question_en="Is the workload balanced across inspectors?",
        question_ar="هل حمل العمل متوازن بين المفتشين؟",
        variations_en=[
            "Workload balance",
            "Inspector workload distribution",
            "Fair workload allocation"
        ],
        variations_ar=["توازن حمل العمل", "توزيع حمل عمل المفتشين"],
        keywords_en=["workload", "balance", "fair", "distribution"],
        keywords_ar=["حمل عمل", "توازن", "عادل", "توزيع"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(COUNT(e.Id) * 100.0 / SUM(COUNT(e.Id)) OVER () AS DECIMAL(5,2)) as workload_share_pct
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="PRED_RES_007",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "OPTIMIZATION"],
        question_en="How can we optimize inspection routes?",
        question_ar="كيف يمكننا تحسين مسارات الفحص؟",
        variations_en=[
            "Route optimization",
            "Efficient inspection paths",
            "Optimize inspector travel"
        ],
        variations_ar=["تحسين المسارات", "مسارات فحص فعالة"],
        keywords_en=["optimize", "route", "efficiency", "travel"],
        keywords_ar=["تحسين", "مسار", "كفاءة", "سفر"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(l.Id) as locations_to_inspect,
                   COUNT(DISTINCT e.ReporterID) as inspectors_active
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY locations_to_inspect DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_008",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "PEAK", "STAFFING"],
        question_en="When do we need the most inspectors?",
        question_ar="متى نحتاج أكبر عدد من المفتشين؟",
        variations_en=[
            "Peak staffing needs",
            "When most inspectors needed",
            "High demand periods"
        ],
        variations_ar=["احتياجات الذروة", "متى نحتاج مفتشين أكثر"],
        keywords_en=["peak", "most", "when", "staffing"],
        keywords_ar=["ذروة", "أكثر", "متى", "توظيف"],
        sql="""
            SELECT DATENAME(WEEKDAY, SubmitionDate) as day_name,
                   DATEPART(WEEKDAY, SubmitionDate) as day_num,
                   DATEPART(HOUR, SubmitionDate) as hour,
                   COUNT(*) as inspections
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY DATENAME(WEEKDAY, SubmitionDate), DATEPART(WEEKDAY, SubmitionDate), DATEPART(HOUR, SubmitionDate)
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_009",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "SPECIALIST"],
        question_en="Which violation categories need specialist inspectors?",
        question_ar="أي فئات المخالفات تحتاج مفتشين متخصصين؟",
        variations_en=[
            "Specialist needs",
            "Expert inspector requirements",
            "Specialized inspection needs"
        ],
        variations_ar=["احتياجات التخصص", "متطلبات مفتشين خبراء"],
        keywords_en=["specialist", "expert", "specialized", "category"],
        keywords_ar=["متخصص", "خبير", "تخصص", "فئة"],
        sql="""
            SELECT vc.Name as category,
                   COUNT(ev.Id) as violation_count,
                   AVG(ev.Value) as avg_severity
            FROM ViolationCategory vc
            JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY violation_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_RES_010",
        category=QuestionCategory.PREDICTION,
        subcategory="resource_planning",
        intent=["RESOURCE", "BUDGET", "PLANNING"],
        question_en="What budget should we plan for inspections?",
        question_ar="ما الميزانية التي يجب التخطيط لها للفحوصات؟",
        variations_en=[
            "Inspection budget planning",
            "Resource budget",
            "Financial planning for inspections"
        ],
        variations_ar=["تخطيط ميزانية الفحوصات", "ميزانية الموارد"],
        keywords_en=["budget", "planning", "financial", "cost"],
        keywords_ar=["ميزانية", "تخطيط", "مالي", "تكلفة"],
        sql="""
            SELECT 
                COUNT(*) as total_inspections,
                COUNT(DISTINCT ReporterID) as inspectors_used,
                SUM(CASE WHEN Score < 80 THEN 1 ELSE 0 END) as failed_inspections,
                (SELECT SUM(Value) FROM EventViolation ev JOIN Event e2 ON ev.EventId = e2.Id WHERE e2.IsDeleted = 0 AND YEAR(e2.SubmitionDate) = {year}) as total_violation_value
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# PERFORMANCE PREDICTION QUESTIONS (10 questions)
# ============================================================================

PERFORMANCE_PREDICTION_QUESTIONS = [
    QuestionTemplate(
        id="PRED_PERF_001",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "INSPECTOR", "PERFORMANCE"],
        question_en="Which inspectors are likely to perform best next month?",
        question_ar="أي المفتشين من المحتمل أن يؤدوا الأفضل الشهر القادم؟",
        variations_en=[
            "Top performing inspectors",
            "Best inspector prediction",
            "Expected top performers"
        ],
        variations_ar=["أفضل المفتشين أداءً", "تنبؤ أفضل المفتشين"],
        keywords_en=["best", "inspector", "performance", "predict"],
        keywords_ar=["أفضل", "مفتش", "أداء", "تنبؤ"],
        sql="""
            SELECT TOP 10 u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(AVG(e.Score) + (COUNT(e.Id) * 0.1) AS DECIMAL(5,2)) as performance_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(e.Id) >= 5
            ORDER BY performance_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_PERF_002",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "LOCATION", "IMPROVEMENT"],
        question_en="Which locations are likely to improve?",
        question_ar="أي المواقع من المحتمل أن تتحسن؟",
        variations_en=[
            "Improving locations prediction",
            "Expected improvements",
            "Locations trending up"
        ],
        variations_ar=["تنبؤ المواقع المتحسنة", "التحسينات المتوقعة"],
        keywords_en=["improve", "location", "prediction", "better"],
        keywords_ar=["تحسن", "موقع", "تنبؤ", "أفضل"],
        sql="""
            WITH RecentTrend AS (
                SELECT e.LocationID,
                       AVG(CASE WHEN e.SubmitionDate >= DATEADD(month, -1, GETDATE()) THEN e.Score END) as recent_avg,
                       AVG(CASE WHEN e.SubmitionDate < DATEADD(month, -1, GETDATE()) AND e.SubmitionDate >= DATEADD(month, -3, GETDATE()) THEN e.Score END) as older_avg
                FROM Event e
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY e.LocationID
            )
            SELECT l.Name as location,
                   CAST(r.recent_avg AS DECIMAL(5,2)) as recent_score,
                   CAST(r.older_avg AS DECIMAL(5,2)) as previous_score,
                   CAST(r.recent_avg - r.older_avg AS DECIMAL(5,2)) as improvement
            FROM RecentTrend r
            JOIN Location l ON r.LocationID = l.Id
            WHERE r.recent_avg > r.older_avg AND r.older_avg IS NOT NULL
            ORDER BY improvement DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_PERF_003",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "GOAL", "ACHIEVEMENT"],
        question_en="Will we achieve our compliance goals this year?",
        question_ar="هل سنحقق أهداف الامتثال هذا العام؟",
        variations_en=[
            "Goal achievement prediction",
            "Will we meet targets?",
            "Annual goal projection"
        ],
        variations_ar=["تنبؤ تحقيق الأهداف", "هل سنحقق الأهداف؟"],
        keywords_en=["goal", "achieve", "target", "predict"],
        keywords_ar=["هدف", "تحقيق", "غاية", "تنبؤ"],
        sql="""
            SELECT 
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as current_compliance,
                85.0 as target_compliance,
                CASE 
                    WHEN SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 85 THEN 'On Track'
                    WHEN SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 80 THEN 'Close'
                    ELSE 'At Risk'
                END as projection
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_PERF_004",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "BOTTLENECK"],
        question_en="Where are performance bottlenecks likely to occur?",
        question_ar="أين من المحتمل أن تحدث اختناقات الأداء؟",
        variations_en=[
            "Bottleneck prediction",
            "Performance constraints",
            "Expected bottlenecks"
        ],
        variations_ar=["تنبؤ الاختناقات", "قيود الأداء"],
        keywords_en=["bottleneck", "constraint", "limitation", "predict"],
        keywords_ar=["اختناق", "قيد", "حد", "تنبؤ"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(DISTINCT l.Id) as locations,
                   COUNT(e.Id) as inspections_ytd,
                   CAST(COUNT(DISTINCT l.Id) * 1.0 / NULLIF(COUNT(e.Id), 0) * 12 AS DECIMAL(5,2)) as coverage_ratio
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            HAVING COUNT(DISTINCT l.Id) > COUNT(e.Id) / 12.0
            ORDER BY coverage_ratio DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_PERF_005",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "PERFORMANCE", "TREND"],
        question_en="What is the predicted performance trend?",
        question_ar="ما هو اتجاه الأداء المتوقع؟",
        variations_en=[
            "Performance trend prediction",
            "Expected performance direction",
            "Future performance outlook"
        ],
        variations_ar=["تنبؤ اتجاه الأداء", "اتجاه الأداء المتوقع"],
        keywords_en=["trend", "performance", "direction", "predict"],
        keywords_ar=["اتجاه", "أداء", "متوقع", "تنبؤ"],
        sql="""
            SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                   COUNT(*) as inspections,
                   CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="PRED_PERF_006",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "QUARTERLY", "PERFORMANCE"],
        question_en="What is the predicted performance for next quarter?",
        question_ar="ما هو الأداء المتوقع للربع القادم؟",
        variations_en=[
            "Next quarter performance",
            "Q+1 prediction",
            "Quarterly forecast"
        ],
        variations_ar=["أداء الربع القادم", "توقعات الربع"],
        keywords_en=["quarter", "next", "performance", "predict"],
        keywords_ar=["ربع", "قادم", "أداء", "تنبؤ"],
        sql="""
            SELECT CONCAT('Q', DATEPART(QUARTER, SubmitionDate)) as quarter,
                   COUNT(*) as inspections,
                   CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY DATEPART(QUARTER, SubmitionDate)
            ORDER BY DATEPART(QUARTER, SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_PERF_007",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "SUCCESS", "RATE"],
        question_en="What is the predicted success rate for new locations?",
        question_ar="ما معدل النجاح المتوقع للمواقع الجديدة؟",
        variations_en=[
            "New location success prediction",
            "First inspection success rate",
            "New site performance"
        ],
        variations_ar=["تنبؤ نجاح المواقع الجديدة", "معدل نجاح الفحص الأول"],
        keywords_en=["success", "new", "location", "predict"],
        keywords_ar=["نجاح", "جديد", "موقع", "تنبؤ"],
        sql="""
            WITH FirstInspections AS (
                SELECT e.*, ROW_NUMBER() OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as rn
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT COUNT(CASE WHEN Score >= 80 THEN 1 END) as passed,
                   COUNT(*) as total,
                   CAST(COUNT(CASE WHEN Score >= 80 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as first_time_pass_rate
            FROM FirstInspections WHERE rn = 1
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_PERF_008",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "TEAM", "PERFORMANCE"],
        question_en="How will the team perform compared to last year?",
        question_ar="كيف سيكون أداء الفريق مقارنة بالعام الماضي؟",
        variations_en=[
            "Team performance prediction",
            "Year over year team comparison",
            "Expected team improvement"
        ],
        variations_ar=["تنبؤ أداء الفريق", "مقارنة الفريق سنوياً"],
        keywords_en=["team", "performance", "compare", "last year"],
        keywords_ar=["فريق", "أداء", "مقارنة", "العام الماضي"],
        sql="""
            SELECT 
                'Current Year' as period,
                COUNT(*) as inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(DISTINCT ReporterID) as active_inspectors
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            UNION ALL
            SELECT 
                'Previous Year',
                COUNT(*),
                CAST(AVG(Score) AS DECIMAL(5,2)),
                COUNT(DISTINCT ReporterID)
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year} - 1
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="PRED_PERF_009",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "RECOVERY", "TIME"],
        question_en="How long will it take for failing locations to recover?",
        question_ar="كم سيستغرق المواقع الفاشلة للتعافي؟",
        variations_en=[
            "Recovery time prediction",
            "Time to compliance",
            "How long to improve"
        ],
        variations_ar=["تنبؤ وقت التعافي", "الوقت للامتثال"],
        keywords_en=["recovery", "time", "how long", "improve"],
        keywords_ar=["تعافي", "وقت", "كم", "تحسن"],
        sql="""
            WITH FailThenPass AS (
                SELECT e.LocationID, e.SubmitionDate as fail_date,
                       (SELECT MIN(e2.SubmitionDate) FROM Event e2 
                        WHERE e2.LocationID = e.LocationID AND e2.Score >= 80 
                        AND e2.SubmitionDate > e.SubmitionDate AND e2.IsDeleted = 0) as pass_date
                FROM Event e
                WHERE e.IsDeleted = 0 AND e.Score < 80 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT AVG(DATEDIFF(day, fail_date, pass_date)) as avg_days_to_recover,
                   MIN(DATEDIFF(day, fail_date, pass_date)) as min_days,
                   MAX(DATEDIFF(day, fail_date, pass_date)) as max_days
            FROM FailThenPass WHERE pass_date IS NOT NULL
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="PRED_PERF_010",
        category=QuestionCategory.PREDICTION,
        subcategory="performance_prediction",
        intent=["PREDICT", "EFFICIENCY", "GAINS"],
        question_en="Where can we expect efficiency gains?",
        question_ar="أين يمكن توقع مكاسب الكفاءة؟",
        variations_en=[
            "Efficiency improvement areas",
            "Expected efficiency gains",
            "Optimization opportunities"
        ],
        variations_ar=["مجالات تحسين الكفاءة", "مكاسب الكفاءة المتوقعة"],
        keywords_en=["efficiency", "gains", "improve", "optimize"],
        keywords_ar=["كفاءة", "مكاسب", "تحسين", "تحسين"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   COUNT(DISTINCT e.ReporterID) as inspectors,
                   CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.ReporterID), 0) AS DECIMAL(5,2)) as inspections_per_inspector
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            HAVING COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.ReporterID), 0) < 
                   (SELECT AVG(insp_per_insp) FROM (
                       SELECT COUNT(e2.Id) * 1.0 / NULLIF(COUNT(DISTINCT e2.ReporterID), 0) as insp_per_insp
                       FROM Location l2
                       JOIN Event e2 ON e2.LocationID = l2.Id
                       WHERE e2.IsDeleted = 0 AND YEAR(e2.SubmitionDate) = {year}
                       GROUP BY l2.NeighborhoodID
                   ) sub)
            ORDER BY inspections_per_inspector ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
]


# ============================================================================
# REGISTER ALL EXTENDED PREDICTION QUESTIONS
# ============================================================================

ALL_EXTENDED_PREDICTION_QUESTIONS = (
    FORECASTING_QUESTIONS +
    RISK_PREDICTION_QUESTIONS +
    ANOMALY_DETECTION_QUESTIONS +
    RESOURCE_PLANNING_QUESTIONS +
    PERFORMANCE_PREDICTION_QUESTIONS
)

# Register all questions
registry.register_many(ALL_EXTENDED_PREDICTION_QUESTIONS)

print(f"Extended Prediction Questions loaded: {len(ALL_EXTENDED_PREDICTION_QUESTIONS)} templates")
