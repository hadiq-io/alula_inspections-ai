"""
Temporal Questions Library
===========================
100+ time-based questions covering daily, weekly, monthly, quarterly, and yearly patterns.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# DAILY PATTERNS (20 questions)
# ============================================================================

DAILY_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_DAY_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "INSPECTIONS", "TODAY"],
        question_en="How many inspections were done today?",
        question_ar="كم عدد الفحوصات التي تمت اليوم؟",
        variations_en=[
            "Today's inspections",
            "Inspections today",
            "Today's inspection count",
            "What happened today?"
        ],
        variations_ar=[
            "فحوصات اليوم",
            "عدد فحوصات اليوم"
        ],
        keywords_en=["today", "inspections", "daily", "how many"],
        keywords_ar=["اليوم", "فحوصات", "يومي", "كم"],
        sql="""
            SELECT 
                COUNT(*) as inspections_today,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations_today
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND CAST(e.SubmitionDate AS DATE) = CAST(GETDATE() AS DATE)
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "VIOLATIONS", "TODAY"],
        question_en="How many violations were found today?",
        question_ar="كم عدد المخالفات المكتشفة اليوم؟",
        variations_en=[
            "Today's violations",
            "Violations found today",
            "Today's violation count"
        ],
        variations_ar=[
            "مخالفات اليوم",
            "عدد مخالفات اليوم"
        ],
        keywords_en=["today", "violations", "found", "how many"],
        keywords_ar=["اليوم", "مخالفات", "مكتشفة", "كم"],
        sql="""
            SELECT 
                COUNT(*) as violations_today,
                SUM(ev.Value) as total_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND CAST(e.SubmitionDate AS DATE) = CAST(GETDATE() AS DATE)
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_003",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "PATTERN", "WEEKDAY"],
        question_en="Which day of the week has the most inspections?",
        question_ar="أي يوم في الأسبوع لديه أكثر فحوصات؟",
        variations_en=[
            "Busiest day of the week",
            "Peak inspection day",
            "Most active weekday"
        ],
        variations_ar=[
            "أكثر أيام الأسبوع نشاطاً",
            "يوم الذروة"
        ],
        keywords_en=["day", "week", "most", "busiest", "peak"],
        keywords_ar=["يوم", "أسبوع", "أكثر", "ذروة"],
        sql="""
            SELECT 
                DATENAME(WEEKDAY, e.SubmitionDate) as day_name,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(WEEKDAY, e.SubmitionDate), DATEPART(WEEKDAY, e.SubmitionDate)
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_004",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "YESTERDAY"],
        question_en="What happened yesterday?",
        question_ar="ماذا حدث أمس؟",
        variations_en=[
            "Yesterday's summary",
            "Yesterday's inspections",
            "What did we do yesterday?"
        ],
        variations_ar=[
            "ملخص أمس",
            "فحوصات أمس"
        ],
        keywords_en=["yesterday", "summary", "what", "happened"],
        keywords_ar=["أمس", "ملخص", "ماذا"],
        sql="""
            SELECT 
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count,
                COUNT(DISTINCT e.ReporterID) as active_inspectors
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND CAST(e.SubmitionDate AS DATE) = CAST(DATEADD(day, -1, GETDATE()) AS DATE)
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# WEEKLY PATTERNS (20 questions)
# ============================================================================

WEEKLY_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_WEEK_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "INSPECTIONS", "THIS_WEEK"],
        question_en="How many inspections this week?",
        question_ar="كم عدد الفحوصات هذا الأسبوع؟",
        variations_en=[
            "This week's inspections",
            "Inspections this week",
            "Weekly inspection count"
        ],
        variations_ar=[
            "فحوصات هذا الأسبوع",
            "عدد الفحوصات الأسبوعية"
        ],
        keywords_en=["this week", "inspections", "weekly", "how many"],
        keywords_ar=["هذا الأسبوع", "فحوصات", "أسبوعي"],
        sql="""
            SELECT 
                COUNT(*) as inspections_this_week,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations_this_week
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND DATEPART(WEEK, e.SubmitionDate) = DATEPART(WEEK, GETDATE())
              AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "TREND"],
        question_en="What is the weekly inspection trend?",
        question_ar="ما هو اتجاه الفحوصات الأسبوعي؟",
        variations_en=[
            "Weekly trend",
            "Inspections by week",
            "Week by week trend"
        ],
        variations_ar=[
            "الاتجاه الأسبوعي",
            "الفحوصات حسب الأسبوع"
        ],
        keywords_en=["weekly", "trend", "by week"],
        keywords_ar=["أسبوعي", "اتجاه"],
        sql="""
            SELECT 
                DATEPART(WEEK, e.SubmitionDate) as week_number,
                MIN(CAST(e.SubmitionDate AS DATE)) as week_start,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.SubmitionDate >= DATEADD(week, -12, GETDATE())
            GROUP BY DATEPART(WEEK, e.SubmitionDate), YEAR(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), week_number
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# MONTHLY PATTERNS (20 questions)
# ============================================================================

MONTHLY_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_MONTH_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTHLY", "INSPECTIONS", "THIS_MONTH"],
        question_en="How many inspections this month?",
        question_ar="كم عدد الفحوصات هذا الشهر؟",
        variations_en=[
            "This month's inspections",
            "Inspections this month",
            "Monthly inspection count"
        ],
        variations_ar=[
            "فحوصات هذا الشهر",
            "عدد الفحوصات الشهرية"
        ],
        keywords_en=["this month", "inspections", "monthly", "how many"],
        keywords_ar=["هذا الشهر", "فحوصات", "شهري"],
        sql="""
            SELECT 
                COUNT(*) as inspections_this_month,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations_this_month,
                COUNT(DISTINCT ReporterID) as active_inspectors
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND MONTH(e.SubmitionDate) = MONTH(GETDATE())
              AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TEXT,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTHLY", "BEST", "WORST"],
        question_en="Which month had the best performance?",
        question_ar="أي شهر كان الأفضل أداءً؟",
        variations_en=[
            "Best performing month",
            "Highest scoring month",
            "Top month for performance"
        ],
        variations_ar=[
            "أفضل شهر أداءً",
            "الشهر الأعلى درجات"
        ],
        keywords_en=["month", "best", "performance", "highest", "top"],
        keywords_ar=["شهر", "أفضل", "أداء"],
        sql="""
            SELECT 
                DATENAME(MONTH, e.SubmitionDate) as month_name,
                MONTH(e.SubmitionDate) as month_number,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(MONTH, e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# QUARTERLY PATTERNS (20 questions)
# ============================================================================

QUARTERLY_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_QUAR_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTERLY", "SUMMARY", "THIS_QUARTER"],
        question_en="What is this quarter's summary?",
        question_ar="ما هو ملخص هذا الربع؟",
        variations_en=[
            "This quarter summary",
            "Quarterly performance",
            "Q summary",
            "Current quarter stats"
        ],
        variations_ar=[
            "ملخص الربع الحالي",
            "أداء هذا الربع"
        ],
        keywords_en=["quarter", "summary", "this quarter", "quarterly"],
        keywords_ar=["ربع", "ملخص", "ربع سنوي"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(QUARTER, GETDATE()), ' ', YEAR(GETDATE())) as current_quarter,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_violation_value
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND DATEPART(QUARTER, e.SubmitionDate) = DATEPART(QUARTER, GETDATE())
              AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QUAR_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTERLY", "TREND", "ALL"],
        question_en="Show me quarterly trends for the year",
        question_ar="أظهر لي اتجاهات الأرباع للسنة",
        variations_en=[
            "Quarterly trend",
            "Q1 Q2 Q3 Q4 comparison",
            "All quarters performance"
        ],
        variations_ar=[
            "اتجاه ربع سنوي",
            "مقارنة جميع الأرباع"
        ],
        keywords_en=["quarterly", "trend", "Q1", "Q2", "Q3", "Q4"],
        keywords_ar=["ربع سنوي", "اتجاه"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(QUARTER, e.SubmitionDate)) as quarter,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(QUARTER, e.SubmitionDate)
            ORDER BY DATEPART(QUARTER, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# YEARLY PATTERNS (20 questions)
# ============================================================================

YEARLY_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_YEAR_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["YEARLY", "SUMMARY", "THIS_YEAR"],
        question_en="What is this year's summary?",
        question_ar="ما هو ملخص هذا العام؟",
        variations_en=[
            "This year summary",
            "Annual summary",
            "Year to date stats",
            "YTD performance"
        ],
        variations_ar=[
            "ملخص هذا العام",
            "الملخص السنوي"
        ],
        keywords_en=["year", "summary", "annual", "ytd", "this year"],
        keywords_ar=["سنة", "ملخص", "سنوي", "هذا العام"],
        sql="""
            SELECT 
                YEAR(GETDATE()) as year,
                COUNT(*) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate,
                COUNT(ev.Id) as total_violations,
                SUM(ev.Value) as total_violation_value,
                COUNT(DISTINCT e.ReporterID) as unique_inspectors,
                COUNT(DISTINCT e.LocationID) as unique_locations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["YEARLY", "COMPARISON", "MULTI_YEAR"],
        question_en="Show me yearly trends over the past 3 years",
        question_ar="أظهر لي الاتجاهات السنوية خلال السنوات الثلاث الماضية",
        variations_en=[
            "Multi-year trend",
            "Year over year trends",
            "Historical yearly data",
            "Past 3 years comparison"
        ],
        variations_ar=[
            "اتجاهات متعددة السنوات",
            "مقارنة سنوية"
        ],
        keywords_en=["yearly", "trend", "years", "historical", "multi-year"],
        keywords_ar=["سنوي", "اتجاه", "تاريخي"],
        sql="""
            SELECT 
                YEAR(e.SubmitionDate) as year,
                COUNT(*) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as total_violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) >= YEAR(GETDATE()) - 2
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
]


# ============================================================================
# REGISTER ALL TEMPORAL QUESTIONS
# ============================================================================

ALL_TEMPORAL_QUESTIONS = (
    DAILY_QUESTIONS +
    WEEKLY_QUESTIONS +
    MONTHLY_QUESTIONS +
    QUARTERLY_QUESTIONS +
    YEARLY_QUESTIONS
)

# Register all questions
registry.register_many(ALL_TEMPORAL_QUESTIONS)

print(f"Temporal Questions loaded: {len(ALL_TEMPORAL_QUESTIONS)} templates")
