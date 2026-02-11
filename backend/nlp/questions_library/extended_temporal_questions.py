"""
Extended Temporal Questions Library
====================================
50+ additional time-based questions covering daily, weekly, monthly,
quarterly, yearly, and seasonal analysis patterns.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# DAILY ANALYSIS QUESTIONS (10 questions)
# ============================================================================

DAILY_ANALYSIS_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_DAY_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["TODAY", "INSPECTIONS"],
        question_en="What inspections happened today?",
        question_ar="ما الفحوصات التي حدثت اليوم؟",
        variations_en=["Today's inspections", "Inspections today", "What happened today?"],
        variations_ar=["فحوصات اليوم", "ماذا حدث اليوم؟"],
        keywords_en=["today", "inspections", "happened"],
        keywords_ar=["اليوم", "فحوصات", "حدث"],
        sql="""
            SELECT e.Id, l.Name as location, e.Score, u.Name as inspector, e.SubmitionDate
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND CAST(e.SubmitionDate AS DATE) = CAST(GETDATE() AS DATE)
            ORDER BY e.SubmitionDate DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["YESTERDAY", "INSPECTIONS"],
        question_en="What inspections happened yesterday?",
        question_ar="ما الفحوصات التي حدثت أمس؟",
        variations_en=["Yesterday's inspections", "Inspections yesterday", "What happened yesterday?"],
        variations_ar=["فحوصات الأمس", "ماذا حدث أمس؟"],
        keywords_en=["yesterday", "inspections", "happened"],
        keywords_ar=["أمس", "فحوصات", "حدث"],
        sql="""
            SELECT e.Id, l.Name as location, e.Score, u.Name as inspector, e.SubmitionDate
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND CAST(e.SubmitionDate AS DATE) = CAST(DATEADD(day, -1, GETDATE()) AS DATE)
            ORDER BY e.SubmitionDate DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_003",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "AVERAGE"],
        question_en="What is the daily average of inspections?",
        question_ar="ما هو المتوسط اليومي للفحوصات؟",
        variations_en=["Daily inspection average", "Average per day", "How many per day?"],
        variations_ar=["متوسط الفحوصات اليومية", "المعدل اليومي"],
        keywords_en=["daily", "average", "per day", "inspections"],
        keywords_ar=["يومي", "متوسط", "في اليوم", "فحوصات"],
        sql="""
            SELECT 
                COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)) as total_days,
                COUNT(e.Id) as total_inspections,
                CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)), 0) AS DECIMAL(5,2)) as avg_per_day
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_004",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["BUSIEST", "DAY"],
        question_en="What was the busiest day?",
        question_ar="ما هو اليوم الأكثر انشغالاً؟",
        variations_en=["Busiest day", "Most inspections in a day", "Peak day"],
        variations_ar=["اليوم الأكثر انشغالاً", "أكثر فحوصات في يوم"],
        keywords_en=["busiest", "day", "most", "peak"],
        keywords_ar=["أكثر", "انشغال", "يوم", "ذروة"],
        sql="""
            SELECT TOP 1 CAST(e.SubmitionDate AS DATE) as date,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CAST(e.SubmitionDate AS DATE)
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_005",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["SPECIFIC", "DATE"],
        question_en="What happened on {date}?",
        question_ar="ماذا حدث في {date}؟",
        variations_en=["On a specific date", "Inspections on date", "That day's activity"],
        variations_ar=["في تاريخ محدد", "فحوصات التاريخ"],
        keywords_en=["on", "date", "specific", "happened"],
        keywords_ar=["في", "تاريخ", "محدد", "حدث"],
        sql="""
            SELECT e.Id, l.Name as location, e.Score, u.Name as inspector
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND CAST(e.SubmitionDate AS DATE) = '{date}'
            ORDER BY e.SubmitionDate
        """,
        parameters={"date": str},
        default_values={"date": "2024-01-15"},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_006",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAY", "OF", "WEEK"],
        question_en="Which day of the week has most inspections?",
        question_ar="أي يوم في الأسبوع لديه أكثر فحوصات؟",
        variations_en=["Best day of week", "Most productive weekday", "Day of week analysis"],
        variations_ar=["أفضل يوم في الأسبوع", "أكثر يوم إنتاجية"],
        keywords_en=["day", "week", "most", "which"],
        keywords_ar=["يوم", "أسبوع", "أكثر", "أي"],
        sql="""
            SELECT DATENAME(weekday, e.SubmitionDate) as day_of_week,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(weekday, e.SubmitionDate), DATEPART(weekday, e.SubmitionDate)
            ORDER BY DATEPART(weekday, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_007",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["LAST", "7", "DAYS"],
        question_en="What happened in the last 7 days?",
        question_ar="ماذا حدث في الأيام السبعة الماضية؟",
        variations_en=["Last week", "Past 7 days", "Recent week activity"],
        variations_ar=["الأسبوع الماضي", "آخر 7 أيام"],
        keywords_en=["last", "7", "days", "week"],
        keywords_ar=["آخر", "7", "أيام", "أسبوع"],
        sql="""
            SELECT CAST(e.SubmitionDate AS DATE) as date,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.SubmitionDate >= DATEADD(day, -7, GETDATE())
            GROUP BY CAST(e.SubmitionDate AS DATE)
            ORDER BY date
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_008",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "VIOLATIONS"],
        question_en="How many violations per day?",
        question_ar="كم عدد المخالفات في اليوم؟",
        variations_en=["Daily violations", "Violations per day", "Daily violation count"],
        variations_ar=["المخالفات اليومية", "مخالفات كل يوم"],
        keywords_en=["daily", "violations", "per day", "count"],
        keywords_ar=["يومي", "مخالفات", "في اليوم", "عدد"],
        sql="""
            SELECT CAST(e.SubmitionDate AS DATE) as date,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year} AND MONTH(e.SubmitionDate) = {month}
            GROUP BY CAST(e.SubmitionDate AS DATE)
            ORDER BY date
        """,
        parameters={"year": int, "month": int},
        default_values={"year": 2024, "month": 6},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_009",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["WORKING", "DAYS"],
        question_en="How many working days had inspections?",
        question_ar="كم عدد أيام العمل التي بها فحوصات؟",
        variations_en=["Active days count", "Days with inspections", "Working days"],
        variations_ar=["عدد الأيام النشطة", "أيام بها فحوصات"],
        keywords_en=["working", "days", "inspections", "count"],
        keywords_ar=["عمل", "أيام", "فحوصات", "عدد"],
        sql="""
            SELECT 
                COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)) as working_days,
                FORMAT(MIN(e.SubmitionDate), 'yyyy-MM-dd') as first_day,
                FORMAT(MAX(e.SubmitionDate), 'yyyy-MM-dd') as last_day
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_DAY_010",
        category=QuestionCategory.TEMPORAL,
        subcategory="daily",
        intent=["DAILY", "BREAKDOWN"],
        question_en="Show daily breakdown for this month",
        question_ar="أظهر التفصيل اليومي لهذا الشهر",
        variations_en=["Daily stats this month", "Day by day this month", "This month daily"],
        variations_ar=["إحصائيات يومية هذا الشهر", "يوم بيوم هذا الشهر"],
        keywords_en=["daily", "breakdown", "this month", "day by day"],
        keywords_ar=["يومي", "تفصيل", "هذا الشهر", "يوم بيوم"],
        sql="""
            SELECT CAST(e.SubmitionDate AS DATE) as date,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = YEAR(GETDATE()) 
                  AND MONTH(e.SubmitionDate) = MONTH(GETDATE())
            GROUP BY CAST(e.SubmitionDate AS DATE)
            ORDER BY date
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# WEEKLY ANALYSIS QUESTIONS (10 questions)
# ============================================================================

WEEKLY_ANALYSIS_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_WEEK_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["THIS", "WEEK"],
        question_en="What happened this week?",
        question_ar="ماذا حدث هذا الأسبوع؟",
        variations_en=["This week's summary", "Weekly summary", "This week inspections"],
        variations_ar=["ملخص هذا الأسبوع", "الملخص الأسبوعي"],
        keywords_en=["this", "week", "summary", "happened"],
        keywords_ar=["هذا", "أسبوع", "ملخص", "حدث"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT e.LocationID) as locations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND e.SubmitionDate >= DATEADD(day, -DATEPART(weekday, GETDATE())+1, CAST(GETDATE() AS DATE))
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["LAST", "WEEK"],
        question_en="What happened last week?",
        question_ar="ماذا حدث الأسبوع الماضي؟",
        variations_en=["Last week's summary", "Previous week", "Last week inspections"],
        variations_ar=["ملخص الأسبوع الماضي", "الأسبوع السابق"],
        keywords_en=["last", "week", "previous", "happened"],
        keywords_ar=["الماضي", "أسبوع", "سابق", "حدث"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND e.SubmitionDate >= DATEADD(week, -1, DATEADD(day, -DATEPART(weekday, GETDATE())+1, CAST(GETDATE() AS DATE)))
                  AND e.SubmitionDate < DATEADD(day, -DATEPART(weekday, GETDATE())+1, CAST(GETDATE() AS DATE))
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_003",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "TREND"],
        question_en="Show weekly trends for the year",
        question_ar="أظهر الاتجاهات الأسبوعية للسنة",
        variations_en=["Weekly trends", "Week by week", "Weekly performance"],
        variations_ar=["الاتجاهات الأسبوعية", "أسبوع بأسبوع"],
        keywords_en=["weekly", "trend", "week", "year"],
        keywords_ar=["أسبوعي", "اتجاه", "أسبوع", "سنة"],
        sql="""
            SELECT DATEPART(week, e.SubmitionDate) as week_number,
                   MIN(CAST(e.SubmitionDate AS DATE)) as week_start,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(week, e.SubmitionDate)
            ORDER BY week_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_WEEK_004",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "COMPARISON"],
        question_en="Compare this week to last week",
        question_ar="قارن هذا الأسبوع بالأسبوع الماضي",
        variations_en=["Week over week", "WoW comparison", "This vs last week"],
        variations_ar=["أسبوع بأسبوع", "هذا مقابل الماضي"],
        keywords_en=["compare", "week", "this", "last"],
        keywords_ar=["مقارنة", "أسبوع", "هذا", "الماضي"],
        sql="""
            SELECT 
                CASE 
                    WHEN e.SubmitionDate >= DATEADD(day, -DATEPART(weekday, GETDATE())+1, CAST(GETDATE() AS DATE)) THEN 'This Week'
                    ELSE 'Last Week'
                END as period,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 
                  AND e.SubmitionDate >= DATEADD(week, -1, DATEADD(day, -DATEPART(weekday, GETDATE())+1, CAST(GETDATE() AS DATE)))
            GROUP BY CASE WHEN e.SubmitionDate >= DATEADD(day, -DATEPART(weekday, GETDATE())+1, CAST(GETDATE() AS DATE)) THEN 'This Week' ELSE 'Last Week' END
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_005",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "AVERAGE"],
        question_en="What is the weekly average?",
        question_ar="ما هو المتوسط الأسبوعي؟",
        variations_en=["Weekly average", "Average per week", "Typical week"],
        variations_ar=["المتوسط الأسبوعي", "المعدل لكل أسبوع"],
        keywords_en=["weekly", "average", "per week", "typical"],
        keywords_ar=["أسبوعي", "متوسط", "لكل أسبوع", "عادي"],
        sql="""
            SELECT 
                COUNT(DISTINCT DATEPART(week, e.SubmitionDate)) as total_weeks,
                COUNT(e.Id) as total_inspections,
                CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT DATEPART(week, e.SubmitionDate)), 0) AS DECIMAL(5,2)) as avg_per_week
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_006",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["BUSIEST", "WEEK"],
        question_en="Which was the busiest week?",
        question_ar="أي أسبوع كان الأكثر انشغالاً؟",
        variations_en=["Busiest week", "Peak week", "Most active week"],
        variations_ar=["الأسبوع الأكثر انشغالاً", "أسبوع الذروة"],
        keywords_en=["busiest", "week", "peak", "most"],
        keywords_ar=["أكثر", "انشغال", "أسبوع", "ذروة"],
        sql="""
            SELECT TOP 1 DATEPART(week, e.SubmitionDate) as week_number,
                   MIN(CAST(e.SubmitionDate AS DATE)) as week_start,
                   COUNT(e.Id) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(week, e.SubmitionDate)
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_007",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKDAY", "VS", "WEEKEND"],
        question_en="Compare weekday vs weekend inspections",
        question_ar="قارن فحوصات أيام الأسبوع بعطلة نهاية الأسبوع",
        variations_en=["Weekday vs weekend", "Business days vs weekends", "Weekend activity"],
        variations_ar=["أيام العمل مقابل العطلة", "نشاط العطلة"],
        keywords_en=["weekday", "weekend", "compare", "business days"],
        keywords_ar=["أيام العمل", "عطلة", "مقارنة"],
        sql="""
            SELECT 
                CASE WHEN DATEPART(weekday, e.SubmitionDate) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END as day_type,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN DATEPART(weekday, e.SubmitionDate) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_008",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "VIOLATIONS"],
        question_en="Show weekly violation trends",
        question_ar="أظهر اتجاهات المخالفات الأسبوعية",
        variations_en=["Weekly violations", "Violations per week", "Weekly violation count"],
        variations_ar=["المخالفات الأسبوعية", "مخالفات كل أسبوع"],
        keywords_en=["weekly", "violations", "trend", "per week"],
        keywords_ar=["أسبوعي", "مخالفات", "اتجاه", "كل أسبوع"],
        sql="""
            SELECT DATEPART(week, e.SubmitionDate) as week_number,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(week, e.SubmitionDate)
            ORDER BY week_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_009",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEK", "SPECIFIC"],
        question_en="What happened in week {week_number}?",
        question_ar="ماذا حدث في الأسبوع {week_number}؟",
        variations_en=["Specific week", "Week details", "That week's activity"],
        variations_ar=["أسبوع محدد", "تفاصيل الأسبوع"],
        keywords_en=["week", "specific", "number", "details"],
        keywords_ar=["أسبوع", "محدد", "رقم", "تفاصيل"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   MIN(CAST(e.SubmitionDate AS DATE)) as week_start,
                   MAX(CAST(e.SubmitionDate AS DATE)) as week_end
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = {year} 
                  AND DATEPART(week, e.SubmitionDate) = {week_number}
        """,
        parameters={"year": int, "week_number": int},
        default_values={"year": 2024, "week_number": 1},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_WEEK_010",
        category=QuestionCategory.TEMPORAL,
        subcategory="weekly",
        intent=["WEEKLY", "INSPECTOR", "BREAKDOWN"],
        question_en="Show weekly breakdown by inspector",
        question_ar="أظهر التفصيل الأسبوعي حسب المفتش",
        variations_en=["Weekly by inspector", "Inspector weekly activity", "Who did what each week"],
        variations_ar=["الأسبوعي حسب المفتش", "نشاط المفتش الأسبوعي"],
        keywords_en=["weekly", "inspector", "breakdown", "by"],
        keywords_ar=["أسبوعي", "مفتش", "تفصيل", "حسب"],
        sql="""
            SELECT u.Name as inspector,
                   DATEPART(week, e.SubmitionDate) as week_number,
                   COUNT(e.Id) as inspections
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, DATEPART(week, e.SubmitionDate)
            ORDER BY u.Name, week_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# MONTHLY ANALYSIS QUESTIONS (10 questions)
# ============================================================================

MONTHLY_ANALYSIS_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_MONTH_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["THIS", "MONTH"],
        question_en="What happened this month?",
        question_ar="ماذا حدث هذا الشهر؟",
        variations_en=["This month summary", "Monthly summary", "This month's inspections"],
        variations_ar=["ملخص هذا الشهر", "الملخص الشهري"],
        keywords_en=["this", "month", "summary", "happened"],
        keywords_ar=["هذا", "شهر", "ملخص", "حدث"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT e.LocationID) as locations,
                   COUNT(DISTINCT e.ReporterID) as inspectors
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
                  AND MONTH(e.SubmitionDate) = MONTH(GETDATE())
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["LAST", "MONTH"],
        question_en="What happened last month?",
        question_ar="ماذا حدث الشهر الماضي؟",
        variations_en=["Last month summary", "Previous month", "Last month's inspections"],
        variations_ar=["ملخص الشهر الماضي", "الشهر السابق"],
        keywords_en=["last", "month", "previous", "happened"],
        keywords_ar=["الماضي", "شهر", "سابق", "حدث"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = YEAR(DATEADD(month, -1, GETDATE()))
                  AND MONTH(e.SubmitionDate) = MONTH(DATEADD(month, -1, GETDATE()))
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_003",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTHLY", "TREND"],
        question_en="Show monthly trends for the year",
        question_ar="أظهر الاتجاهات الشهرية للسنة",
        variations_en=["Monthly trends", "Month by month", "Monthly performance"],
        variations_ar=["الاتجاهات الشهرية", "شهر بشهر"],
        keywords_en=["monthly", "trend", "month", "year"],
        keywords_ar=["شهري", "اتجاه", "شهر", "سنة"],
        sql="""
            SELECT MONTH(e.SubmitionDate) as month_number,
                   DATENAME(month, e.SubmitionDate) as month_name,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY MONTH(e.SubmitionDate), DATENAME(month, e.SubmitionDate)
            ORDER BY month_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_004",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["SPECIFIC", "MONTH"],
        question_en="What happened in {month_name}?",
        question_ar="ماذا حدث في {month_name}؟",
        variations_en=["Specific month", "Month details", "That month's activity"],
        variations_ar=["شهر محدد", "تفاصيل الشهر"],
        keywords_en=["in", "month", "specific", "happened"],
        keywords_ar=["في", "شهر", "محدد", "حدث"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT e.LocationID) as locations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = {year}
                  AND MONTH(e.SubmitionDate) = {month}
        """,
        parameters={"year": int, "month": int},
        default_values={"year": 2024, "month": 6},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_005",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["BEST", "MONTH"],
        question_en="Which was the best month?",
        question_ar="أي شهر كان الأفضل؟",
        variations_en=["Best performing month", "Highest scoring month", "Top month"],
        variations_ar=["الشهر الأفضل أداءً", "الشهر الأعلى درجة"],
        keywords_en=["best", "month", "highest", "top"],
        keywords_ar=["أفضل", "شهر", "أعلى"],
        sql="""
            SELECT TOP 1 MONTH(e.SubmitionDate) as month_number,
                   DATENAME(month, e.SubmitionDate) as month_name,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY MONTH(e.SubmitionDate), DATENAME(month, e.SubmitionDate)
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_006",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["WORST", "MONTH"],
        question_en="Which was the worst month?",
        question_ar="أي شهر كان الأسوأ؟",
        variations_en=["Worst performing month", "Lowest scoring month", "Bottom month"],
        variations_ar=["الشهر الأسوأ أداءً", "الشهر الأدنى درجة"],
        keywords_en=["worst", "month", "lowest", "bottom"],
        keywords_ar=["أسوأ", "شهر", "أدنى"],
        sql="""
            SELECT TOP 1 MONTH(e.SubmitionDate) as month_number,
                   DATENAME(month, e.SubmitionDate) as month_name,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY MONTH(e.SubmitionDate), DATENAME(month, e.SubmitionDate)
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_007",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTH", "OVER", "MONTH"],
        question_en="Show month over month comparison",
        question_ar="أظهر مقارنة شهر بشهر",
        variations_en=["MoM comparison", "Monthly comparison", "Month by month change"],
        variations_ar=["مقارنة شهرية", "التغيير شهر بشهر"],
        keywords_en=["month", "over", "comparison", "change"],
        keywords_ar=["شهر", "مقارنة", "تغيير"],
        sql="""
            SELECT MONTH(e.SubmitionDate) as month_number,
                   DATENAME(month, e.SubmitionDate) as month_name,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(AVG(e.Score) - LAG(AVG(e.Score)) OVER (ORDER BY MONTH(e.SubmitionDate)) AS DECIMAL(5,2)) as change_from_prev
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY MONTH(e.SubmitionDate), DATENAME(month, e.SubmitionDate)
            ORDER BY month_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_MONTH_008",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTHLY", "VIOLATIONS"],
        question_en="Show monthly violation trends",
        question_ar="أظهر اتجاهات المخالفات الشهرية",
        variations_en=["Monthly violations", "Violations per month", "Monthly violation count"],
        variations_ar=["المخالفات الشهرية", "مخالفات كل شهر"],
        keywords_en=["monthly", "violations", "trend", "per month"],
        keywords_ar=["شهري", "مخالفات", "اتجاه", "كل شهر"],
        sql="""
            SELECT MONTH(e.SubmitionDate) as month_number,
                   DATENAME(month, e.SubmitionDate) as month_name,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY MONTH(e.SubmitionDate), DATENAME(month, e.SubmitionDate)
            ORDER BY month_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_MONTH_009",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTHLY", "BY", "NEIGHBORHOOD"],
        question_en="Show monthly breakdown by neighborhood",
        question_ar="أظهر التفصيل الشهري حسب الحي",
        variations_en=["Monthly by neighborhood", "Neighborhood monthly activity", "Monthly area breakdown"],
        variations_ar=["الشهري حسب الحي", "نشاط الحي الشهري"],
        keywords_en=["monthly", "neighborhood", "breakdown", "by"],
        keywords_ar=["شهري", "حي", "تفصيل", "حسب"],
        sql="""
            SELECT n.Name as neighborhood,
                   MONTH(e.SubmitionDate) as month_number,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, MONTH(e.SubmitionDate)
            ORDER BY n.Name, month_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_MONTH_010",
        category=QuestionCategory.TEMPORAL,
        subcategory="monthly",
        intent=["MONTHLY", "AVERAGE"],
        question_en="What is the monthly average?",
        question_ar="ما هو المتوسط الشهري؟",
        variations_en=["Monthly average", "Average per month", "Typical month"],
        variations_ar=["المتوسط الشهري", "المعدل لكل شهر"],
        keywords_en=["monthly", "average", "per month", "typical"],
        keywords_ar=["شهري", "متوسط", "لكل شهر", "عادي"],
        sql="""
            SELECT 
                COUNT(DISTINCT FORMAT(e.SubmitionDate, 'yyyy-MM')) as total_months,
                COUNT(e.Id) as total_inspections,
                CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT FORMAT(e.SubmitionDate, 'yyyy-MM')), 0) AS DECIMAL(5,2)) as avg_per_month
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# QUARTERLY ANALYSIS QUESTIONS (10 questions)
# ============================================================================

QUARTERLY_ANALYSIS_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_QTR_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["THIS", "QUARTER"],
        question_en="What happened this quarter?",
        question_ar="ماذا حدث هذا الربع؟",
        variations_en=["This quarter summary", "Quarterly summary", "Current quarter"],
        variations_ar=["ملخص هذا الربع", "الملخص الربعي"],
        keywords_en=["this", "quarter", "summary", "current"],
        keywords_ar=["هذا", "ربع", "ملخص", "حالي"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
                  AND DATEPART(quarter, e.SubmitionDate) = DATEPART(quarter, GETDATE())
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QTR_002",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["LAST", "QUARTER"],
        question_en="What happened last quarter?",
        question_ar="ماذا حدث الربع الماضي؟",
        variations_en=["Last quarter summary", "Previous quarter", "Prior quarter"],
        variations_ar=["ملخص الربع الماضي", "الربع السابق"],
        keywords_en=["last", "quarter", "previous", "prior"],
        keywords_ar=["الماضي", "ربع", "سابق"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND (
                      (YEAR(e.SubmitionDate) = YEAR(GETDATE()) AND DATEPART(quarter, e.SubmitionDate) = DATEPART(quarter, GETDATE()) - 1)
                      OR
                      (DATEPART(quarter, GETDATE()) = 1 AND YEAR(e.SubmitionDate) = YEAR(GETDATE()) - 1 AND DATEPART(quarter, e.SubmitionDate) = 4)
                  )
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QTR_003",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTERLY", "TREND"],
        question_en="Show quarterly trends",
        question_ar="أظهر الاتجاهات الربعية",
        variations_en=["Quarterly trends", "Quarter by quarter", "Quarterly performance"],
        variations_ar=["الاتجاهات الربعية", "ربع بربع"],
        keywords_en=["quarterly", "trend", "quarter", "performance"],
        keywords_ar=["ربعي", "اتجاه", "ربع", "أداء"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(quarter, e.SubmitionDate)
            ORDER BY DATEPART(quarter, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QTR_004",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTER", "COMPARISON"],
        question_en="Compare Q1 and Q2",
        question_ar="قارن الربع الأول والثاني",
        variations_en=["Q1 vs Q2", "First vs second quarter", "Quarter comparison"],
        variations_ar=["الربع الأول مقابل الثاني", "مقارنة ربعية"],
        keywords_en=["compare", "Q1", "Q2", "quarter"],
        keywords_ar=["مقارنة", "الربع الأول", "الربع الثاني"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = {year}
                  AND DATEPART(quarter, e.SubmitionDate) IN (1, 2)
            GROUP BY DATEPART(quarter, e.SubmitionDate)
            ORDER BY DATEPART(quarter, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QTR_005",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["BEST", "QUARTER"],
        question_en="Which was the best quarter?",
        question_ar="أي ربع كان الأفضل؟",
        variations_en=["Best quarter", "Highest performing quarter", "Top quarter"],
        variations_ar=["أفضل ربع", "الربع الأعلى أداءً"],
        keywords_en=["best", "quarter", "highest", "top"],
        keywords_ar=["أفضل", "ربع", "أعلى"],
        sql="""
            SELECT TOP 1 
                CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(quarter, e.SubmitionDate)
            ORDER BY AVG(e.Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QTR_006",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTERLY", "BY", "INSPECTOR"],
        question_en="Show quarterly breakdown by inspector",
        question_ar="أظهر التفصيل الربعي حسب المفتش",
        variations_en=["Quarterly by inspector", "Inspector quarterly activity", "Quarter by inspector"],
        variations_ar=["الربعي حسب المفتش", "نشاط المفتش الربعي"],
        keywords_en=["quarterly", "inspector", "breakdown", "by"],
        keywords_ar=["ربعي", "مفتش", "تفصيل", "حسب"],
        sql="""
            SELECT u.Name as inspector,
                   CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, DATEPART(quarter, e.SubmitionDate)
            ORDER BY u.Name, DATEPART(quarter, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_QTR_007",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTERLY", "VIOLATIONS"],
        question_en="Show quarterly violation trends",
        question_ar="أظهر اتجاهات المخالفات الربعية",
        variations_en=["Quarterly violations", "Violations per quarter", "Quarterly violation count"],
        variations_ar=["المخالفات الربعية", "مخالفات كل ربع"],
        keywords_en=["quarterly", "violations", "trend", "per quarter"],
        keywords_ar=["ربعي", "مخالفات", "اتجاه", "كل ربع"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(quarter, e.SubmitionDate)
            ORDER BY DATEPART(quarter, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_QTR_008",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTER", "OVER", "QUARTER"],
        question_en="Show quarter over quarter change",
        question_ar="أظهر التغيير من ربع لربع",
        variations_en=["QoQ change", "Quarter over quarter", "Quarterly change"],
        variations_ar=["التغيير الربعي", "ربع بربع"],
        keywords_en=["quarter", "over", "change", "QoQ"],
        keywords_ar=["ربع", "تغيير"],
        sql="""
            SELECT 
                CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(AVG(e.Score) - LAG(AVG(e.Score)) OVER (ORDER BY DATEPART(quarter, e.SubmitionDate)) AS DECIMAL(5,2)) as change_from_prev
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(quarter, e.SubmitionDate)
            ORDER BY DATEPART(quarter, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_QTR_009",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["QUARTERLY", "BY", "NEIGHBORHOOD"],
        question_en="Show quarterly breakdown by neighborhood",
        question_ar="أظهر التفصيل الربعي حسب الحي",
        variations_en=["Quarterly by neighborhood", "Area quarterly activity", "Quarter by area"],
        variations_ar=["الربعي حسب الحي", "نشاط المنطقة الربعي"],
        keywords_en=["quarterly", "neighborhood", "breakdown", "by"],
        keywords_ar=["ربعي", "حي", "تفصيل", "حسب"],
        sql="""
            SELECT n.Name as neighborhood,
                   CONCAT('Q', DATEPART(quarter, e.SubmitionDate)) as quarter,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, DATEPART(quarter, e.SubmitionDate)
            ORDER BY n.Name, DATEPART(quarter, e.SubmitionDate)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_QTR_010",
        category=QuestionCategory.TEMPORAL,
        subcategory="quarterly",
        intent=["SPECIFIC", "QUARTER"],
        question_en="What happened in Q{quarter}?",
        question_ar="ماذا حدث في الربع {quarter}؟",
        variations_en=["Specific quarter", "Quarter details", "That quarter's activity"],
        variations_ar=["ربع محدد", "تفاصيل الربع"],
        keywords_en=["Q1", "Q2", "Q3", "Q4", "quarter", "specific"],
        keywords_ar=["الربع الأول", "الربع الثاني", "الربع الثالث", "الربع الرابع", "ربع", "محدد"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT e.LocationID) as locations,
                   COUNT(DISTINCT e.ReporterID) as inspectors
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = {year}
                  AND DATEPART(quarter, e.SubmitionDate) = {quarter}
        """,
        parameters={"year": int, "quarter": int},
        default_values={"year": 2024, "quarter": 1},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# YEARLY AND SEASONAL ANALYSIS QUESTIONS (10 questions)
# ============================================================================

YEARLY_SEASONAL_QUESTIONS = [
    QuestionTemplate(
        id="TEMP_YEAR_001",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["THIS", "YEAR"],
        question_en="What happened this year?",
        question_ar="ماذا حدث هذا العام؟",
        variations_en=["This year summary", "Annual summary", "Year to date"],
        variations_ar=["ملخص هذا العام", "الملخص السنوي"],
        keywords_en=["this", "year", "annual", "summary"],
        keywords_ar=["هذا", "عام", "سنوي", "ملخص"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT e.LocationID) as locations,
                   COUNT(DISTINCT e.ReporterID) as inspectors
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
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
        intent=["LAST", "YEAR"],
        question_en="What happened last year?",
        question_ar="ماذا حدث العام الماضي؟",
        variations_en=["Last year summary", "Previous year", "Prior year"],
        variations_ar=["ملخص العام الماضي", "العام السابق"],
        keywords_en=["last", "year", "previous", "prior"],
        keywords_ar=["الماضي", "عام", "سابق"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = YEAR(GETDATE()) - 1
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_003",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["YEAR", "OVER", "YEAR"],
        question_en="Compare this year to last year",
        question_ar="قارن هذا العام بالعام الماضي",
        variations_en=["YoY comparison", "Year over year", "Annual comparison"],
        variations_ar=["مقارنة سنوية", "عام بعام"],
        keywords_en=["compare", "year", "YoY", "annual"],
        keywords_ar=["مقارنة", "عام", "سنوي"],
        sql="""
            SELECT YEAR(e.SubmitionDate) as year,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) IN (YEAR(GETDATE()), YEAR(GETDATE()) - 1)
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_004",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["MULTI", "YEAR", "TREND"],
        question_en="Show multi-year trends",
        question_ar="أظهر اتجاهات متعددة السنوات",
        variations_en=["Multi-year trends", "Historical trends", "Long term trends"],
        variations_ar=["اتجاهات متعددة السنوات", "الاتجاهات التاريخية"],
        keywords_en=["multi", "year", "trend", "historical"],
        keywords_ar=["متعدد", "سنوات", "اتجاه", "تاريخي"],
        sql="""
            SELECT YEAR(e.SubmitionDate) as year,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_005",
        category=QuestionCategory.TEMPORAL,
        subcategory="seasonal",
        intent=["SEASONAL", "PATTERN"],
        question_en="What are the seasonal patterns?",
        question_ar="ما هي الأنماط الموسمية؟",
        variations_en=["Seasonal patterns", "Season by season", "Seasonal trends"],
        variations_ar=["الأنماط الموسمية", "فصل بفصل"],
        keywords_en=["seasonal", "pattern", "season", "trends"],
        keywords_ar=["موسمي", "نمط", "فصل", "اتجاهات"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                          WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                          WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                          ELSE 'Fall' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_006",
        category=QuestionCategory.TEMPORAL,
        subcategory="seasonal",
        intent=["SUMMER", "VS", "WINTER"],
        question_en="Compare summer vs winter performance",
        question_ar="قارن أداء الصيف بالشتاء",
        variations_en=["Summer vs winter", "Hot vs cold season", "Seasonal comparison"],
        variations_ar=["الصيف مقابل الشتاء", "مقارنة موسمية"],
        keywords_en=["summer", "winter", "compare", "season"],
        keywords_ar=["صيف", "شتاء", "مقارنة", "موسم"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                END as season,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) = {year}
                  AND MONTH(e.SubmitionDate) IN (12, 1, 2, 6, 7, 8)
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                          WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_007",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["YEAR", "TO", "DATE"],
        question_en="Show year-to-date progress",
        question_ar="أظهر التقدم منذ بداية العام",
        variations_en=["YTD progress", "Year to date", "Progress so far"],
        variations_ar=["التقدم منذ بداية العام", "حتى الآن"],
        keywords_en=["year", "to", "date", "YTD", "progress"],
        keywords_ar=["عام", "حتى", "تاريخ", "تقدم"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(e.Id) as inspections,
                SUM(COUNT(e.Id)) OVER (ORDER BY FORMAT(e.SubmitionDate, 'yyyy-MM')) as cumulative_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = YEAR(GETDATE())
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_YEAR_008",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["ANNUAL", "BY", "INSPECTOR"],
        question_en="Show annual breakdown by inspector",
        question_ar="أظهر التفصيل السنوي حسب المفتش",
        variations_en=["Annual by inspector", "Inspector yearly activity", "Year by inspector"],
        variations_ar=["السنوي حسب المفتش", "نشاط المفتش السنوي"],
        keywords_en=["annual", "inspector", "breakdown", "year"],
        keywords_ar=["سنوي", "مفتش", "تفصيل", "عام"],
        sql="""
            SELECT u.Name as inspector,
                   YEAR(e.SubmitionDate) as year,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
            GROUP BY u.Id, u.Name, YEAR(e.SubmitionDate)
            ORDER BY u.Name, year
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="TEMP_YEAR_009",
        category=QuestionCategory.TEMPORAL,
        subcategory="seasonal",
        intent=["PEAK", "SEASON"],
        question_en="When is the peak season?",
        question_ar="متى موسم الذروة؟",
        variations_en=["Peak season", "Busiest season", "When are we busiest?"],
        variations_ar=["موسم الذروة", "أكثر موسم انشغالاً"],
        keywords_en=["peak", "season", "busiest", "when"],
        keywords_ar=["ذروة", "موسم", "أكثر انشغالاً", "متى"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(e.Id) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                          WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                          WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                          ELSE 'Fall' END
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="TEMP_YEAR_010",
        category=QuestionCategory.TEMPORAL,
        subcategory="yearly",
        intent=["SPECIFIC", "YEAR"],
        question_en="What happened in year {year}?",
        question_ar="ماذا حدث في عام {year}؟",
        variations_en=["Specific year", "Year details", "That year's activity"],
        variations_ar=["عام محدد", "تفاصيل العام"],
        keywords_en=["in", "year", "specific", "happened"],
        keywords_ar=["في", "عام", "محدد", "حدث"],
        sql="""
            SELECT COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT e.LocationID) as locations,
                   COUNT(DISTINCT e.ReporterID) as inspectors
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]


# ============================================================================
# REGISTER ALL EXTENDED TEMPORAL QUESTIONS
# ============================================================================

ALL_EXTENDED_TEMPORAL_QUESTIONS = (
    DAILY_ANALYSIS_QUESTIONS +
    WEEKLY_ANALYSIS_QUESTIONS +
    MONTHLY_ANALYSIS_QUESTIONS +
    QUARTERLY_ANALYSIS_QUESTIONS +
    YEARLY_SEASONAL_QUESTIONS
)

# Register all questions
registry.register_many(ALL_EXTENDED_TEMPORAL_QUESTIONS)

print(f"Extended Temporal Questions loaded: {len(ALL_EXTENDED_TEMPORAL_QUESTIONS)} templates")
