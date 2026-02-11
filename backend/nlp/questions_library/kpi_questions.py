"""
KPI Questions Library
======================
100+ KPI-related questions covering compliance, performance, violations, risk, and efficiency.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# COMPLIANCE KPIs (20 questions)
# ============================================================================

COMPLIANCE_QUESTIONS = [
    QuestionTemplate(
        id="KPI_COMP_001",
        category=QuestionCategory.KPI,
        subcategory="compliance",
        intent=["RATE", "PERCENTAGE"],
        question_en="What is the current compliance rate?",
        question_ar="ما هو معدل الامتثال الحالي؟",
        variations_en=[
            "Show me the compliance rate",
            "What's our compliance percentage?",
            "How compliant are we?",
            "Compliance rate please",
            "What is the overall compliance?"
        ],
        variations_ar=[
            "أظهر لي معدل الامتثال",
            "ما نسبة الامتثال لدينا؟",
            "كم نسبة الالتزام؟"
        ],
        keywords_en=["compliance", "rate", "percentage", "compliant"],
        keywords_ar=["امتثال", "نسبة", "معدل", "التزام"],
        sql="""
            SELECT 
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        show_calculation_steps=True,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_COMP_002",
        category=QuestionCategory.KPI,
        subcategory="compliance",
        intent=["TREND", "MONTHLY"],
        question_en="What is the monthly compliance trend?",
        question_ar="ما هو اتجاه الامتثال الشهري؟",
        variations_en=[
            "Show compliance by month",
            "Monthly compliance rate",
            "How has compliance changed over months?",
            "Compliance trend over time"
        ],
        variations_ar=[
            "أظهر الامتثال حسب الشهر",
            "معدل الامتثال الشهري",
            "كيف تغير الامتثال خلال الأشهر؟"
        ],
        keywords_en=["compliance", "trend", "monthly", "over time"],
        keywords_ar=["امتثال", "اتجاه", "شهري"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_COMP_003",
        category=QuestionCategory.KPI,
        subcategory="compliance",
        intent=["COMPARE", "LOCATION"],
        question_en="What is the compliance rate by neighborhood?",
        question_ar="ما هو معدل الامتثال حسب الحي؟",
        variations_en=[
            "Compliance by area",
            "Which neighborhoods are most compliant?",
            "Show compliance per neighborhood",
            "Neighborhood compliance rates"
        ],
        variations_ar=[
            "الامتثال حسب المنطقة",
            "أي الأحياء أكثر امتثالاً؟"
        ],
        keywords_en=["compliance", "neighborhood", "area", "location", "by area"],
        keywords_ar=["امتثال", "حي", "منطقة"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(*) as total_inspections,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY compliance_rate DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_COMP_004",
        category=QuestionCategory.KPI,
        subcategory="compliance",
        intent=["COUNT", "NON_COMPLIANT"],
        question_en="How many non-compliant inspections are there?",
        question_ar="كم عدد الفحوصات غير الممتثلة؟",
        variations_en=[
            "Number of failed inspections",
            "Count of non-compliant inspections",
            "How many inspections failed?",
            "Non-compliance count"
        ],
        variations_ar=[
            "عدد الفحوصات الفاشلة",
            "كم فحص غير ممتثل؟"
        ],
        keywords_en=["non-compliant", "failed", "failing", "non-compliance"],
        keywords_ar=["غير ممتثل", "فاشل", "عدم امتثال"],
        sql="""
            SELECT 
                COUNT(*) as non_compliant_count,
                CAST(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM Event WHERE IsDeleted = 0 AND Score IS NOT NULL AND YEAR(SubmitionDate) = {year}), 0) AS DECIMAL(5,2)) as percentage
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND e.Score < 80
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_COMP_005",
        category=QuestionCategory.KPI,
        subcategory="compliance",
        intent=["TREND", "QUARTERLY"],
        question_en="What is the quarterly compliance trend?",
        question_ar="ما هو اتجاه الامتثال الربع سنوي؟",
        variations_en=[
            "Compliance by quarter",
            "Quarterly compliance rate",
            "Q1 Q2 Q3 Q4 compliance"
        ],
        variations_ar=[
            "الامتثال حسب الربع",
            "معدل الامتثال الربع سنوي"
        ],
        keywords_en=["compliance", "quarterly", "quarter", "Q1", "Q2", "Q3", "Q4"],
        keywords_ar=["امتثال", "ربع سنوي", "ربع"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(QUARTER, e.SubmitionDate)) as quarter,
                COUNT(*) as total_inspections,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(QUARTER, e.SubmitionDate)
            ORDER BY DATEPART(QUARTER, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# PERFORMANCE KPIs (20 questions)
# ============================================================================

PERFORMANCE_QUESTIONS = [
    QuestionTemplate(
        id="KPI_PERF_001",
        category=QuestionCategory.KPI,
        subcategory="performance",
        intent=["COUNT", "TOTAL"],
        question_en="What is the total number of inspections?",
        question_ar="ما هو إجمالي عدد الفحوصات؟",
        variations_en=[
            "How many inspections total?",
            "Total inspections count",
            "Number of inspections",
            "Count of all inspections",
            "Show total inspections"
        ],
        variations_ar=[
            "كم عدد الفحوصات؟",
            "إجمالي الفحوصات",
            "عدد كل الفحوصات"
        ],
        keywords_en=["total", "inspections", "count", "number", "how many"],
        keywords_ar=["إجمالي", "فحوصات", "عدد", "كم"],
        sql="""
            SELECT COUNT(*) as total_inspections
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_PERF_002",
        category=QuestionCategory.KPI,
        subcategory="performance",
        intent=["AVERAGE", "SCORE"],
        question_en="What is the average inspection score?",
        question_ar="ما هو متوسط درجة الفحص؟",
        variations_en=[
            "Average score",
            "Mean inspection score",
            "What's the avg score?",
            "Overall average score"
        ],
        variations_ar=[
            "متوسط الدرجات",
            "المعدل العام للدرجات"
        ],
        keywords_en=["average", "score", "mean", "avg"],
        keywords_ar=["متوسط", "درجة", "معدل"],
        sql="""
            SELECT 
                CAST(AVG(Score) AS DECIMAL(5,2)) as average_score,
                MIN(Score) as min_score,
                MAX(Score) as max_score
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        show_calculation_steps=True,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_PERF_003",
        category=QuestionCategory.KPI,
        subcategory="performance",
        intent=["COUNT", "INSPECTOR"],
        question_en="How many active inspectors are there?",
        question_ar="كم عدد المفتشين النشطين؟",
        variations_en=[
            "Number of inspectors",
            "Active inspectors count",
            "How many inspectors working?",
            "Count of active inspectors"
        ],
        variations_ar=[
            "عدد المفتشين",
            "المفتشين النشطين",
            "كم مفتش يعمل؟"
        ],
        keywords_en=["inspectors", "active", "count", "working"],
        keywords_ar=["مفتشين", "نشطين", "عدد"],
        sql="""
            SELECT COUNT(DISTINCT ReporterID) as active_inspectors
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.ReporterID IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_PERF_004",
        category=QuestionCategory.KPI,
        subcategory="performance",
        intent=["RATE", "COMPLETION"],
        question_en="What is the inspection completion rate?",
        question_ar="ما هو معدل إكمال الفحوصات؟",
        variations_en=[
            "Completion rate",
            "How many inspections completed?",
            "Percentage of completed inspections",
            "Inspection completion percentage"
        ],
        variations_ar=[
            "معدل الإكمال",
            "نسبة الفحوصات المكتملة"
        ],
        keywords_en=["completion", "rate", "completed", "finished"],
        keywords_ar=["إكمال", "معدل", "مكتملة"],
        sql="""
            SELECT 
                COUNT(*) as total_inspections,
                SUM(CASE WHEN EventStatusLookupId IN (4, 5) THEN 1 ELSE 0 END) as completed,
                CAST(SUM(CASE WHEN EventStatusLookupId IN (4, 5) THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as completion_rate
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        show_calculation_steps=True,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_PERF_005",
        category=QuestionCategory.KPI,
        subcategory="performance",
        intent=["AVERAGE", "DAILY"],
        question_en="What is the average number of inspections per day?",
        question_ar="ما هو متوسط عدد الفحوصات يومياً؟",
        variations_en=[
            "Daily average inspections",
            "Inspections per day",
            "How many inspections per day?",
            "Average daily inspections"
        ],
        variations_ar=[
            "متوسط الفحوصات اليومية",
            "الفحوصات في اليوم"
        ],
        keywords_en=["daily", "average", "per day", "inspections"],
        keywords_ar=["يومي", "متوسط", "في اليوم"],
        sql="""
            SELECT 
                CAST(AVG(daily_count) AS DECIMAL(10,2)) as avg_per_day,
                MIN(daily_count) as min_per_day,
                MAX(daily_count) as max_per_day
            FROM (
                SELECT CAST(SubmitionDate AS DATE) as date, COUNT(*) as daily_count
                FROM Event e
                WHERE e.IsDeleted = 0
                  AND YEAR(e.SubmitionDate) = {year}
                GROUP BY CAST(SubmitionDate AS DATE)
            ) daily
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        show_calculation_steps=True,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_PERF_006",
        category=QuestionCategory.KPI,
        subcategory="performance",
        intent=["RANKING", "INSPECTOR"],
        question_en="Who are the top performing inspectors?",
        question_ar="من هم أفضل المفتشين أداءً؟",
        variations_en=[
            "Best inspectors",
            "Top inspectors by performance",
            "Inspector rankings",
            "Highest performing inspectors",
            "Top 10 inspectors"
        ],
        variations_ar=[
            "أفضل المفتشين",
            "ترتيب المفتشين",
            "المفتشين الأعلى أداءً"
        ],
        keywords_en=["top", "best", "performing", "inspectors", "ranking"],
        keywords_ar=["أفضل", "أداء", "مفتشين", "ترتيب"],
        sql="""
            SELECT TOP 10
                r.Name as inspector_name,
                COUNT(*) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            JOIN [User] r ON e.ReporterID = r.Id
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY r.Id, r.Name
            HAVING COUNT(*) >= 10
            ORDER BY avg_score DESC, total_inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# VIOLATIONS KPIs (20 questions)
# ============================================================================

VIOLATIONS_QUESTIONS = [
    QuestionTemplate(
        id="KPI_VIOL_001",
        category=QuestionCategory.KPI,
        subcategory="violations",
        intent=["COUNT", "TOTAL"],
        question_en="What is the total number of violations?",
        question_ar="ما هو إجمالي عدد المخالفات؟",
        variations_en=[
            "How many violations?",
            "Total violations count",
            "Number of violations",
            "Count all violations",
            "Violations total"
        ],
        variations_ar=[
            "كم عدد المخالفات؟",
            "إجمالي المخالفات",
            "عدد كل المخالفات"
        ],
        keywords_en=["violations", "total", "count", "number", "how many"],
        keywords_ar=["مخالفات", "إجمالي", "عدد", "كم"],
        sql="""
            SELECT COUNT(*) as total_violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_VIOL_002",
        category=QuestionCategory.KPI,
        subcategory="violations",
        intent=["VALUE", "MONETARY"],
        question_en="What is the total value of violations?",
        question_ar="ما هو إجمالي قيمة المخالفات؟",
        variations_en=[
            "Total violation value",
            "Monetary value of violations",
            "How much in violations?",
            "Total fines amount",
            "Violations financial value"
        ],
        variations_ar=[
            "قيمة المخالفات",
            "إجمالي الغرامات",
            "كم قيمة المخالفات؟"
        ],
        keywords_en=["value", "violations", "monetary", "amount", "fines", "financial"],
        keywords_ar=["قيمة", "مخالفات", "غرامات", "مالية"],
        sql="""
            SELECT 
                SUM(ev.Value) as total_value,
                COUNT(*) as violation_count,
                AVG(ev.Value) as avg_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        show_calculation_steps=True,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_VIOL_003",
        category=QuestionCategory.KPI,
        subcategory="violations",
        intent=["RANKING", "TYPE"],
        question_en="What are the most common violation types?",
        question_ar="ما هي أكثر أنواع المخالفات شيوعاً؟",
        variations_en=[
            "Top violation types",
            "Most frequent violations",
            "Common violations",
            "Violation types ranking",
            "Which violations occur most?"
        ],
        variations_ar=[
            "أكثر المخالفات شيوعاً",
            "أنواع المخالفات الأكثر",
            "ترتيب أنواع المخالفات"
        ],
        keywords_en=["common", "violation", "types", "frequent", "most", "ranking"],
        keywords_ar=["شيوعاً", "مخالفات", "أنواع", "أكثر"],
        sql="""
            SELECT TOP 10
                vt.Name as violation_type,
                vt.NameAr as violation_type_ar,
                COUNT(*) as count,
                SUM(ev.Value) as total_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name, vt.NameAr
            ORDER BY count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_VIOL_004",
        category=QuestionCategory.KPI,
        subcategory="violations",
        intent=["COUNT", "CRITICAL"],
        question_en="How many critical violations are there?",
        question_ar="كم عدد المخالفات الحرجة؟",
        variations_en=[
            "Critical violations count",
            "Number of critical issues",
            "Severe violations",
            "High severity violations",
            "Major violations count"
        ],
        variations_ar=[
            "المخالفات الحرجة",
            "عدد المخالفات الخطيرة",
            "المخالفات الشديدة"
        ],
        keywords_en=["critical", "violations", "severe", "major", "high severity"],
        keywords_ar=["حرجة", "خطيرة", "شديدة", "مخالفات"],
        sql="""
            SELECT 
                COUNT(*) as critical_count,
                SUM(ev.Value) as total_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND ev.SeverityLevel >= 3
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_VIOL_005",
        category=QuestionCategory.KPI,
        subcategory="violations",
        intent=["TREND", "MONTHLY"],
        question_en="What is the monthly violation trend?",
        question_ar="ما هو اتجاه المخالفات الشهري؟",
        variations_en=[
            "Violations by month",
            "Monthly violation count",
            "Violation trend over time",
            "How are violations trending?"
        ],
        variations_ar=[
            "المخالفات حسب الشهر",
            "اتجاه المخالفات الشهري"
        ],
        keywords_en=["monthly", "trend", "violations", "over time"],
        keywords_ar=["شهري", "اتجاه", "مخالفات"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(*) as violation_count,
                SUM(ev.Value) as total_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_VIOL_006",
        category=QuestionCategory.KPI,
        subcategory="violations",
        intent=["DISTRIBUTION", "SEVERITY"],
        question_en="What is the distribution of violations by severity?",
        question_ar="ما هو توزيع المخالفات حسب الخطورة؟",
        variations_en=[
            "Violations by severity level",
            "Severity distribution",
            "How are violations distributed by severity?",
            "Breakdown by severity"
        ],
        variations_ar=[
            "توزيع المخالفات حسب الخطورة",
            "المخالفات حسب مستوى الخطورة"
        ],
        keywords_en=["distribution", "severity", "violations", "level", "breakdown"],
        keywords_ar=["توزيع", "خطورة", "مخالفات", "مستوى"],
        sql="""
            SELECT 
                CASE ev.SeverityLevel
                    WHEN 1 THEN 'Low'
                    WHEN 2 THEN 'Medium'
                    WHEN 3 THEN 'High'
                    WHEN 4 THEN 'Critical'
                    ELSE 'Unknown'
                END as severity,
                COUNT(*) as count,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY ev.SeverityLevel
            ORDER BY ev.SeverityLevel
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# RISK KPIs (20 questions)
# ============================================================================

RISK_QUESTIONS = [
    QuestionTemplate(
        id="KPI_RISK_001",
        category=QuestionCategory.KPI,
        subcategory="risk",
        intent=["RANKING", "LOCATION"],
        question_en="What are the highest risk locations?",
        question_ar="ما هي المواقع الأعلى خطورة؟",
        variations_en=[
            "High risk locations",
            "Most risky locations",
            "Locations with most violations",
            "Problem locations",
            "Top risk areas"
        ],
        variations_ar=[
            "المواقع عالية الخطورة",
            "المواقع الأكثر خطورة",
            "المواقع التي بها أكثر مخالفات"
        ],
        keywords_en=["risk", "locations", "high", "risky", "problem", "areas"],
        keywords_ar=["خطورة", "مواقع", "عالية", "مشكلة"],
        sql="""
            SELECT TOP 10
                l.Name as location_name,
                n.Name as neighborhood,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_value,
                AVG(e.Score) as avg_score
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            GROUP BY l.Id, l.Name, n.Name
            HAVING COUNT(ev.Id) > 0
            ORDER BY violation_count DESC, total_value DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_RISK_002",
        category=QuestionCategory.KPI,
        subcategory="risk",
        intent=["RATE", "RECURRENCE"],
        question_en="What is the violation recurrence rate?",
        question_ar="ما هو معدل تكرار المخالفات؟",
        variations_en=[
            "Recurrence rate",
            "Repeat violations rate",
            "How often do violations recur?",
            "Violation repeat rate"
        ],
        variations_ar=[
            "معدل التكرار",
            "نسبة تكرار المخالفات"
        ],
        keywords_en=["recurrence", "repeat", "rate", "violations", "recurring"],
        keywords_ar=["تكرار", "معدل", "مخالفات"],
        sql="""
            WITH LocationViolations AS (
                SELECT 
                    e.LocationID,
                    COUNT(*) as violation_count
                FROM EventViolation ev
                JOIN Event e ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0
                  AND YEAR(e.SubmitionDate) = {year}
                GROUP BY e.LocationID
            )
            SELECT 
                COUNT(CASE WHEN violation_count > 1 THEN 1 END) as locations_with_recurrence,
                COUNT(*) as total_locations,
                CAST(COUNT(CASE WHEN violation_count > 1 THEN 1 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as recurrence_rate
            FROM LocationViolations
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        show_calculation_steps=True,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="KPI_RISK_003",
        category=QuestionCategory.KPI,
        subcategory="risk",
        intent=["SCORE", "AVERAGE"],
        question_en="What is the average risk score?",
        question_ar="ما هو متوسط درجة الخطورة؟",
        variations_en=[
            "Average risk score",
            "Mean risk level",
            "Overall risk score",
            "Risk score average"
        ],
        variations_ar=[
            "متوسط درجة الخطورة",
            "المعدل العام للخطورة"
        ],
        keywords_en=["risk", "score", "average", "mean", "level"],
        keywords_ar=["خطورة", "درجة", "متوسط"],
        sql="""
            SELECT 
                CAST(AVG(CAST(ev.SeverityLevel AS FLOAT)) AS DECIMAL(5,2)) as avg_risk_score,
                COUNT(*) as total_violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# EFFICIENCY KPIs (20 questions)
# ============================================================================

EFFICIENCY_QUESTIONS = [
    QuestionTemplate(
        id="KPI_EFF_001",
        category=QuestionCategory.KPI,
        subcategory="efficiency",
        intent=["AVERAGE", "INSPECTOR"],
        question_en="What is the average inspections per inspector?",
        question_ar="ما هو متوسط الفحوصات لكل مفتش؟",
        variations_en=[
            "Inspections per inspector",
            "Inspector workload",
            "Average inspector load",
            "How many inspections per inspector?"
        ],
        variations_ar=[
            "الفحوصات لكل مفتش",
            "حمل عمل المفتش"
        ],
        keywords_en=["inspections", "per", "inspector", "average", "workload"],
        keywords_ar=["فحوصات", "مفتش", "متوسط", "حمل عمل"],
        sql="""
            SELECT 
                CAST(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT ReporterID), 0) AS DECIMAL(10,2)) as avg_per_inspector,
                COUNT(*) as total_inspections,
                COUNT(DISTINCT ReporterID) as inspector_count
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.ReporterID IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        show_calculation_steps=True,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_EFF_002",
        category=QuestionCategory.KPI,
        subcategory="efficiency",
        intent=["COVERAGE", "LOCATION"],
        question_en="What is the location coverage rate?",
        question_ar="ما هو معدل تغطية المواقع؟",
        variations_en=[
            "Location coverage",
            "How many locations inspected?",
            "Coverage percentage",
            "Locations visited rate"
        ],
        variations_ar=[
            "تغطية المواقع",
            "نسبة المواقع المفحوصة"
        ],
        keywords_en=["coverage", "locations", "rate", "visited", "inspected"],
        keywords_ar=["تغطية", "مواقع", "نسبة", "مفحوصة"],
        sql="""
            SELECT 
                COUNT(DISTINCT e.LocationID) as locations_inspected,
                (SELECT COUNT(*) FROM Location WHERE IsDeleted = 0) as total_locations,
                CAST(COUNT(DISTINCT e.LocationID) * 100.0 / 
                     NULLIF((SELECT COUNT(*) FROM Location WHERE IsDeleted = 0), 0) AS DECIMAL(5,2)) as coverage_rate
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        show_calculation_steps=True,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_EFF_003",
        category=QuestionCategory.KPI,
        subcategory="efficiency",
        intent=["AVERAGE", "TIME"],
        question_en="What is the average resolution time?",
        question_ar="ما هو متوسط وقت الحل؟",
        variations_en=[
            "Resolution time",
            "Average time to resolve",
            "How long to resolve issues?",
            "Time to resolution"
        ],
        variations_ar=[
            "وقت الحل",
            "متوسط وقت الحل"
        ],
        keywords_en=["resolution", "time", "average", "resolve", "duration"],
        keywords_ar=["حل", "وقت", "متوسط"],
        sql="""
            SELECT 
                AVG(DATEDIFF(day, e.SubmitionDate, e.UpdatedAt)) as avg_resolution_days,
                MIN(DATEDIFF(day, e.SubmitionDate, e.UpdatedAt)) as min_days,
                MAX(DATEDIFF(day, e.SubmitionDate, e.UpdatedAt)) as max_days
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.EventStatusLookupId IN (4, 5)  -- Completed statuses
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        show_calculation_steps=True,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# DASHBOARD & SUMMARY KPIs (20 questions)
# ============================================================================

DASHBOARD_QUESTIONS = [
    QuestionTemplate(
        id="KPI_DASH_001",
        category=QuestionCategory.KPI,
        subcategory="dashboard",
        intent=["SUMMARY", "OVERVIEW"],
        question_en="Show me the KPI dashboard",
        question_ar="أظهر لي لوحة المؤشرات",
        variations_en=[
            "KPI dashboard",
            "Show dashboard",
            "Overall summary",
            "Key metrics overview",
            "Main KPIs",
            "Executive summary"
        ],
        variations_ar=[
            "لوحة المؤشرات",
            "ملخص عام",
            "المؤشرات الرئيسية"
        ],
        keywords_en=["dashboard", "kpi", "summary", "overview", "metrics", "main"],
        keywords_ar=["لوحة", "مؤشرات", "ملخص", "رئيسية"],
        sql="""
            SELECT 
                (SELECT COUNT(*) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as total_inspections,
                (SELECT COUNT(*) FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}) as total_violations,
                (SELECT CAST(AVG(Score) AS DECIMAL(5,2)) FROM Event WHERE IsDeleted = 0 AND Score IS NOT NULL AND YEAR(SubmitionDate) = {year}) as avg_score,
                (SELECT CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) FROM Event WHERE IsDeleted = 0 AND Score IS NOT NULL AND YEAR(SubmitionDate) = {year}) as compliance_rate,
                (SELECT COUNT(DISTINCT ReporterID) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as active_inspectors,
                (SELECT SUM(Value) FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}) as total_violation_value
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_DASH_002",
        category=QuestionCategory.KPI,
        subcategory="dashboard",
        intent=["COMPARE", "YEAR"],
        question_en="Compare this year with last year",
        question_ar="قارن هذا العام بالعام الماضي",
        variations_en=[
            "Year over year comparison",
            "YoY comparison",
            "This year vs last year",
            "Annual comparison",
            "Compare with previous year"
        ],
        variations_ar=[
            "مقارنة سنوية",
            "مقارنة مع العام السابق"
        ],
        keywords_en=["compare", "year", "yoy", "annual", "previous", "last year"],
        keywords_ar=["مقارنة", "سنوية", "سابق", "العام الماضي"],
        sql="""
            SELECT 
                'Current Year' as period,
                COUNT(*) as total_inspections,
                (SELECT COUNT(*) FROM EventViolation ev2 JOIN Event e2 ON ev2.EventId = e2.Id WHERE e2.IsDeleted = 0 AND YEAR(e2.SubmitionDate) = {year}) as total_violations,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            
            UNION ALL
            
            SELECT 
                'Previous Year' as period,
                COUNT(*) as total_inspections,
                (SELECT COUNT(*) FROM EventViolation ev2 JOIN Event e2 ON ev2.EventId = e2.Id WHERE e2.IsDeleted = 0 AND YEAR(e2.SubmitionDate) = {year} - 1) as total_violations,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year} - 1
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]


# ============================================================================
# REGISTER ALL KPI QUESTIONS
# ============================================================================

ALL_KPI_QUESTIONS = (
    COMPLIANCE_QUESTIONS +
    PERFORMANCE_QUESTIONS +
    VIOLATIONS_QUESTIONS +
    RISK_QUESTIONS +
    EFFICIENCY_QUESTIONS +
    DASHBOARD_QUESTIONS
)

# Register all questions
registry.register_many(ALL_KPI_QUESTIONS)

print(f"KPI Questions loaded: {len(ALL_KPI_QUESTIONS)} templates")
