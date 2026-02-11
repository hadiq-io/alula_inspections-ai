"""
Comparison Questions Library
==============================
150+ comparison-related questions covering time periods, locations, inspectors, and categories.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# TIME PERIOD COMPARISONS (40 questions)
# ============================================================================

TIME_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_TIME_001",
        category=QuestionCategory.COMPARISON,
        subcategory="time_periods",
        intent=["COMPARE", "YEAR", "VIOLATIONS"],
        question_en="Compare violations this year vs last year",
        question_ar="قارن المخالفات هذا العام مع العام الماضي",
        variations_en=[
            "This year vs last year violations",
            "YoY violation comparison",
            "Year over year violations",
            "Compare annual violations"
        ],
        variations_ar=[
            "مقارنة المخالفات السنوية",
            "هذا العام مقابل العام الماضي"
        ],
        keywords_en=["compare", "year", "violations", "vs", "yoy", "annual"],
        keywords_ar=["قارن", "سنة", "مخالفات", "مقابل"],
        sql="""
            SELECT 
                YEAR(e.SubmitionDate) as year,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_value
            FROM Event e
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) IN ({year}, {year} - 1)
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_TIME_002",
        category=QuestionCategory.COMPARISON,
        subcategory="time_periods",
        intent=["COMPARE", "QUARTER", "PERFORMANCE"],
        question_en="Compare this quarter with the previous quarter",
        question_ar="قارن هذا الربع مع الربع السابق",
        variations_en=[
            "QoQ comparison",
            "Quarter over quarter",
            "This quarter vs last quarter",
            "Quarterly comparison"
        ],
        variations_ar=[
            "مقارنة ربع سنوية",
            "هذا الربع مقابل السابق"
        ],
        keywords_en=["compare", "quarter", "qoq", "quarterly", "vs"],
        keywords_ar=["قارن", "ربع", "ربع سنوي"],
        sql="""
            WITH QuarterlyStats AS (
                SELECT 
                    YEAR(e.SubmitionDate) as year,
                    DATEPART(QUARTER, e.SubmitionDate) as quarter,
                    COUNT(*) as inspection_count,
                    AVG(e.Score) as avg_score,
                    COUNT(ev.Id) as violation_count
                FROM Event e
                LEFT JOIN EventViolation ev ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0
                  AND e.SubmitionDate >= DATEADD(month, -6, GETDATE())
                GROUP BY YEAR(e.SubmitionDate), DATEPART(QUARTER, e.SubmitionDate)
            )
            SELECT 
                CONCAT('Q', quarter, ' ', year) as period,
                inspection_count,
                CAST(avg_score AS DECIMAL(5,2)) as avg_score,
                violation_count
            FROM QuarterlyStats
            ORDER BY year DESC, quarter DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_TIME_003",
        category=QuestionCategory.COMPARISON,
        subcategory="time_periods",
        intent=["COMPARE", "MONTH", "INSPECTIONS"],
        question_en="Compare this month with last month",
        question_ar="قارن هذا الشهر مع الشهر الماضي",
        variations_en=[
            "MoM comparison",
            "Month over month",
            "This month vs last month",
            "Monthly comparison"
        ],
        variations_ar=[
            "مقارنة شهرية",
            "هذا الشهر مقابل الماضي"
        ],
        keywords_en=["compare", "month", "mom", "monthly", "vs"],
        keywords_ar=["قارن", "شهر", "شهري"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND e.SubmitionDate >= DATEADD(month, -2, GETDATE())
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_TIME_004",
        category=QuestionCategory.COMPARISON,
        subcategory="time_periods",
        intent=["COMPARE", "WEEK", "ACTIVITY"],
        question_en="Compare this week with last week",
        question_ar="قارن هذا الأسبوع مع الأسبوع الماضي",
        variations_en=[
            "WoW comparison",
            "Week over week",
            "This week vs last week",
            "Weekly comparison"
        ],
        variations_ar=[
            "مقارنة أسبوعية",
            "هذا الأسبوع مقابل الماضي"
        ],
        keywords_en=["compare", "week", "wow", "weekly", "vs"],
        keywords_ar=["قارن", "أسبوع", "أسبوعي"],
        sql="""
            SELECT 
                CASE 
                    WHEN DATEPART(WEEK, e.SubmitionDate) = DATEPART(WEEK, GETDATE()) 
                         AND YEAR(e.SubmitionDate) = YEAR(GETDATE()) 
                    THEN 'This Week'
                    ELSE 'Last Week'
                END as period,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND e.SubmitionDate >= DATEADD(week, -2, GETDATE())
            GROUP BY CASE 
                    WHEN DATEPART(WEEK, e.SubmitionDate) = DATEPART(WEEK, GETDATE()) 
                         AND YEAR(e.SubmitionDate) = YEAR(GETDATE()) 
                    THEN 'This Week'
                    ELSE 'Last Week'
                END
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# LOCATION COMPARISONS (40 questions)
# ============================================================================

LOCATION_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_LOC_001",
        category=QuestionCategory.COMPARISON,
        subcategory="locations",
        intent=["COMPARE", "NEIGHBORHOOD", "PERFORMANCE"],
        question_en="Compare performance between neighborhoods",
        question_ar="قارن الأداء بين الأحياء",
        variations_en=[
            "Neighborhood comparison",
            "Compare areas",
            "Which neighborhood is better?",
            "Area performance comparison"
        ],
        variations_ar=[
            "مقارنة الأحياء",
            "أي حي أفضل؟"
        ],
        keywords_en=["compare", "neighborhood", "area", "performance", "between"],
        keywords_ar=["قارن", "حي", "أداء", "بين"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) as compliance_rate,
                COUNT(ev.Id) as violation_count
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_LOC_002",
        category=QuestionCategory.COMPARISON,
        subcategory="locations",
        intent=["COMPARE", "SPECIFIC_NEIGHBORHOODS"],
        question_en="Compare neighborhood A with neighborhood B",
        question_ar="قارن الحي أ مع الحي ب",
        variations_en=[
            "Compare two neighborhoods",
            "Side by side area comparison",
            "Neighborhood A vs B"
        ],
        variations_ar=[
            "مقارنة حيين",
            "مقارنة منطقتين"
        ],
        keywords_en=["compare", "neighborhood", "vs", "versus"],
        keywords_ar=["قارن", "حي", "مقابل"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_violation_value
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
              AND n.Name IN ('{neighborhood1}', '{neighborhood2}')
            GROUP BY n.Id, n.Name
        """,
        parameters={"year": int, "neighborhood1": str, "neighborhood2": str},
        default_values={"year": 2024, "neighborhood1": "", "neighborhood2": ""},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_LOC_003",
        category=QuestionCategory.COMPARISON,
        subcategory="locations",
        intent=["COMPARE", "TOP_BOTTOM", "LOCATIONS"],
        question_en="Compare top performing vs bottom performing locations",
        question_ar="قارن المواقع الأفضل أداءً مع الأسوأ",
        variations_en=[
            "Best vs worst locations",
            "Top vs bottom performers",
            "High vs low performing"
        ],
        variations_ar=[
            "الأفضل مقابل الأسوأ",
            "المواقع العليا مقابل الدنيا"
        ],
        keywords_en=["compare", "top", "bottom", "best", "worst", "performing"],
        keywords_ar=["قارن", "أفضل", "أسوأ", "أداء"],
        sql="""
            WITH RankedLocations AS (
                SELECT 
                    l.Name as location_name,
                    n.Name as neighborhood,
                    CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                    COUNT(*) as inspection_count,
                    ROW_NUMBER() OVER (ORDER BY AVG(e.Score) DESC) as rank_top,
                    ROW_NUMBER() OVER (ORDER BY AVG(e.Score) ASC) as rank_bottom
                FROM Location l
                JOIN Neighborhood n ON l.NeighborhoodId = n.Id
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0
                  AND e.Score IS NOT NULL
                  AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id, l.Name, n.Name
                HAVING COUNT(*) >= 3
            )
            SELECT 
                location_name,
                neighborhood,
                avg_score,
                inspection_count,
                CASE WHEN rank_top <= 5 THEN 'Top 5' ELSE 'Bottom 5' END as category
            FROM RankedLocations
            WHERE rank_top <= 5 OR rank_bottom <= 5
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# INSPECTOR COMPARISONS (40 questions)
# ============================================================================

INSPECTOR_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_INSP_001",
        category=QuestionCategory.COMPARISON,
        subcategory="inspectors",
        intent=["COMPARE", "INSPECTOR", "PERFORMANCE"],
        question_en="Compare inspector performance",
        question_ar="قارن أداء المفتشين",
        variations_en=[
            "Inspector comparison",
            "Who performs better?",
            "Compare inspectors",
            "Inspector rankings comparison"
        ],
        variations_ar=[
            "مقارنة المفتشين",
            "من أفضل أداءً؟"
        ],
        keywords_en=["compare", "inspector", "performance", "who", "better"],
        keywords_ar=["قارن", "مفتش", "أداء"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) as compliance_rate,
                COUNT(ev.Id) as violations_found
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(*) >= 10
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_INSP_002",
        category=QuestionCategory.COMPARISON,
        subcategory="inspectors",
        intent=["COMPARE", "INSPECTOR", "PRODUCTIVITY"],
        question_en="Compare inspector productivity",
        question_ar="قارن إنتاجية المفتشين",
        variations_en=[
            "Inspector productivity comparison",
            "Who is most productive?",
            "Compare inspector output",
            "Productivity rankings"
        ],
        variations_ar=[
            "مقارنة إنتاجية المفتشين",
            "من الأكثر إنتاجية؟"
        ],
        keywords_en=["compare", "inspector", "productivity", "output", "most"],
        keywords_ar=["قارن", "مفتش", "إنتاجية"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                COUNT(*) as total_inspections,
                COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)) as active_days,
                CAST(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)), 0) AS DECIMAL(5,2)) as inspections_per_day
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(*) >= 10
            ORDER BY total_inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_003",
        category=QuestionCategory.COMPARISON,
        subcategory="inspectors",
        intent=["COMPARE", "INSPECTOR", "CONSISTENCY"],
        question_en="Compare inspector consistency",
        question_ar="قارن اتساق المفتشين",
        variations_en=[
            "Inspector consistency comparison",
            "Who is most consistent?",
            "Score consistency by inspector",
            "Variance in inspector scores"
        ],
        variations_ar=[
            "مقارنة اتساق المفتشين",
            "من الأكثر اتساقاً؟"
        ],
        keywords_en=["compare", "inspector", "consistency", "consistent", "variance"],
        keywords_ar=["قارن", "مفتش", "اتساق"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(STDEV(e.Score) AS DECIMAL(5,2)) as score_std_dev,
                MIN(e.Score) as min_score,
                MAX(e.Score) as max_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(*) >= 20
            ORDER BY score_std_dev ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.ADVANCED
    ),
]

# ============================================================================
# CATEGORY COMPARISONS (30 questions)
# ============================================================================

CATEGORY_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_CAT_001",
        category=QuestionCategory.COMPARISON,
        subcategory="categories",
        intent=["COMPARE", "VIOLATION", "CATEGORIES"],
        question_en="Compare violation categories",
        question_ar="قارن فئات المخالفات",
        variations_en=[
            "Violation category comparison",
            "Compare types of violations",
            "Which category has most violations?",
            "Category breakdown comparison"
        ],
        variations_ar=[
            "مقارنة فئات المخالفات",
            "أي فئة لديها أكثر مخالفات؟"
        ],
        keywords_en=["compare", "violation", "category", "categories", "types"],
        keywords_ar=["قارن", "مخالفات", "فئات", "أنواع"],
        sql="""
            SELECT 
                COALESCE(CAST(ev.QuestionSectionId AS VARCHAR), 'Unspecified') as category,
                COUNT(*) as violation_count,
                SUM(ev.ViolationValue) as total_value,
                AVG(CAST(ev.ViolationValue AS FLOAT)) as avg_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY ev.QuestionSectionId
            ORDER BY violation_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_CAT_002",
        category=QuestionCategory.COMPARISON,
        subcategory="categories",
        intent=["COMPARE", "SEVERITY", "LEVELS"],
        question_en="Compare violations by severity level",
        question_ar="قارن المخالفات حسب مستوى الخطورة",
        variations_en=[
            "Severity comparison",
            "Compare by severity",
            "How do severities compare?",
            "Severity level breakdown"
        ],
        variations_ar=[
            "مقارنة الخطورة",
            "المخالفات حسب الخطورة"
        ],
        keywords_en=["compare", "severity", "level", "levels", "critical"],
        keywords_ar=["قارن", "خطورة", "مستوى"],
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
                SUM(ev.Value) as total_value,
                AVG(ev.Value) as avg_value
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
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]


# ============================================================================
# REGISTER ALL COMPARISON QUESTIONS
# ============================================================================

ALL_COMPARISON_QUESTIONS = (
    TIME_COMPARISON_QUESTIONS +
    LOCATION_COMPARISON_QUESTIONS +
    INSPECTOR_COMPARISON_QUESTIONS +
    CATEGORY_COMPARISON_QUESTIONS
)

# Register all questions
registry.register_many(ALL_COMPARISON_QUESTIONS)

print(f"Comparison Questions loaded: {len(ALL_COMPARISON_QUESTIONS)} templates")
