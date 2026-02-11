"""
Extended Comparison Questions Library
======================================
50+ additional comparison questions covering time-based, entity-based,
benchmark, and various analytical comparisons.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# TIME COMPARISON QUESTIONS (10 questions)
# ============================================================================

TIME_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_TIME_001",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "YEAR"],
        question_en="Compare this year to last year",
        question_ar="قارن هذا العام بالعام الماضي",
        variations_en=["Year over year comparison", "This year vs last year", "Annual comparison"],
        variations_ar=["مقارنة سنوية", "هذا العام مقابل العام الماضي"],
        keywords_en=["compare", "year", "last", "this"],
        keywords_ar=["مقارنة", "عام", "الماضي", "هذا"],
        sql="""
            SELECT 
                YEAR(e.SubmitionDate) as year,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(DISTINCT e.LocationID) as locations_covered
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) IN ({year}, {year}-1)
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
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
        subcategory="time_comparison",
        intent=["COMPARE", "QUARTER"],
        question_en="Compare Q1 and Q2 performance",
        question_ar="قارن أداء الربع الأول والثاني",
        variations_en=["Quarter comparison", "Q1 vs Q2", "First half quarters"],
        variations_ar=["مقارنة ربعية", "الربع الأول مقابل الثاني"],
        keywords_en=["compare", "quarter", "Q1", "Q2"],
        keywords_ar=["مقارنة", "ربع", "الأول", "الثاني"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) <= 3 THEN 'Q1'
                    WHEN MONTH(e.SubmitionDate) <= 6 THEN 'Q2'
                    WHEN MONTH(e.SubmitionDate) <= 9 THEN 'Q3'
                    ELSE 'Q4'
                END as quarter,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) <= 3 THEN 'Q1'
                          WHEN MONTH(e.SubmitionDate) <= 6 THEN 'Q2'
                          WHEN MONTH(e.SubmitionDate) <= 9 THEN 'Q3'
                          ELSE 'Q4' END
            ORDER BY quarter
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_TIME_003",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "MONTH"],
        question_en="Compare month {month1} to month {month2}",
        question_ar="قارن شهر {month1} بشهر {month2}",
        variations_en=["Month comparison", "Compare two months", "Monthly comparison"],
        variations_ar=["مقارنة شهرية", "قارن شهرين"],
        keywords_en=["compare", "month", "months"],
        keywords_ar=["مقارنة", "شهر", "أشهر"],
        sql="""
            SELECT MONTH(e.SubmitionDate) as month,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                  AND MONTH(e.SubmitionDate) IN ({month1}, {month2})
            GROUP BY MONTH(e.SubmitionDate)
        """,
        parameters={"year": int, "month1": int, "month2": int},
        default_values={"year": 2024, "month1": 1, "month2": 6},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_TIME_004",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "WEEK"],
        question_en="Compare this week to last week",
        question_ar="قارن هذا الأسبوع بالأسبوع الماضي",
        variations_en=["Week over week", "This week vs last week", "Weekly comparison"],
        variations_ar=["أسبوع بأسبوع", "هذا الأسبوع مقابل الماضي"],
        keywords_en=["compare", "week", "last", "this"],
        keywords_ar=["مقارنة", "أسبوع", "الماضي", "هذا"],
        sql="""
            SELECT 
                CASE 
                    WHEN e.SubmitionDate >= DATEADD(week, -1, GETDATE()) THEN 'This Week'
                    ELSE 'Last Week'
                END as period,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 
                  AND e.SubmitionDate >= DATEADD(week, -2, GETDATE())
            GROUP BY CASE WHEN e.SubmitionDate >= DATEADD(week, -1, GETDATE()) THEN 'This Week' ELSE 'Last Week' END
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_TIME_005",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "FIRST", "SECOND", "HALF"],
        question_en="Compare first half to second half of the year",
        question_ar="قارن النصف الأول بالنصف الثاني من السنة",
        variations_en=["H1 vs H2", "First half vs second half", "Semi-annual comparison"],
        variations_ar=["النصف الأول مقابل الثاني", "مقارنة نصف سنوية"],
        keywords_en=["compare", "first", "second", "half"],
        keywords_ar=["مقارنة", "أول", "ثاني", "نصف"],
        sql="""
            SELECT 
                CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN 'H1' ELSE 'H2' END as half_year,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN 'H1' ELSE 'H2' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_TIME_006",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "BEFORE", "AFTER"],
        question_en="Compare performance before and after month {month}",
        question_ar="قارن الأداء قبل وبعد شهر {month}",
        variations_en=["Before vs after", "Pre and post comparison", "Split comparison"],
        variations_ar=["قبل مقابل بعد", "مقارنة ما قبل وبعد"],
        keywords_en=["compare", "before", "after", "month"],
        keywords_ar=["مقارنة", "قبل", "بعد", "شهر"],
        sql="""
            SELECT 
                CASE WHEN MONTH(e.SubmitionDate) < {month} THEN 'Before' ELSE 'After' END as period,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) < {month} THEN 'Before' ELSE 'After' END
        """,
        parameters={"year": int, "month": int},
        default_values={"year": 2024, "month": 6},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_TIME_007",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "SAME", "PERIOD"],
        question_en="Compare same period last year",
        question_ar="قارن نفس الفترة من العام الماضي",
        variations_en=["Same period comparison", "YTD vs last YTD", "Period over period"],
        variations_ar=["مقارنة الفترة نفسها", "السنة حتى تاريخه"],
        keywords_en=["compare", "same", "period", "last year"],
        keywords_ar=["مقارنة", "نفس", "فترة", "العام الماضي"],
        sql="""
            SELECT 
                YEAR(e.SubmitionDate) as year,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 
                  AND MONTH(e.SubmitionDate) <= MONTH(GETDATE())
                  AND YEAR(e.SubmitionDate) IN ({year}, {year}-1)
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_TIME_008",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["TREND", "THREE", "YEARS"],
        question_en="Show 3-year trend comparison",
        question_ar="أظهر مقارنة اتجاه ثلاث سنوات",
        variations_en=["Multi-year trend", "Three year comparison", "Historical trend"],
        variations_ar=["اتجاه متعدد السنوات", "مقارنة ثلاث سنوات"],
        keywords_en=["trend", "three", "years", "comparison"],
        keywords_ar=["اتجاه", "ثلاث", "سنوات", "مقارنة"],
        sql="""
            SELECT 
                YEAR(e.SubmitionDate) as year,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 
                  AND YEAR(e.SubmitionDate) >= {year} - 2
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_TIME_009",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["COMPARE", "SEASONAL"],
        question_en="Compare performance across seasons",
        question_ar="قارن الأداء عبر الفصول",
        variations_en=["Seasonal comparison", "Season by season", "Winter vs summer"],
        variations_ar=["مقارنة موسمية", "فصل بفصل"],
        keywords_en=["compare", "seasonal", "season", "winter", "summer"],
        keywords_ar=["مقارنة", "موسمي", "فصل", "شتاء", "صيف"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
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
        id="COMP_TIME_010",
        category=QuestionCategory.COMPARISON,
        subcategory="time_comparison",
        intent=["PROGRESS", "MONTHLY"],
        question_en="Show month-over-month progress",
        question_ar="أظهر التقدم من شهر لآخر",
        variations_en=["MoM progress", "Monthly progress", "Month by month"],
        variations_ar=["التقدم الشهري", "شهر بشهر"],
        keywords_en=["progress", "monthly", "month", "over"],
        keywords_ar=["تقدم", "شهري", "شهر"],
        sql="""
            SELECT FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# INSPECTOR COMPARISON QUESTIONS (10 questions)
# ============================================================================

INSPECTOR_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_INSP_001",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTORS"],
        question_en="Compare all inspectors",
        question_ar="قارن جميع المفتشين",
        variations_en=["Inspector comparison", "Compare inspectors", "All inspectors compared"],
        variations_ar=["مقارنة المفتشين", "قارن المفتشين"],
        keywords_en=["compare", "inspectors", "all"],
        keywords_ar=["مقارنة", "مفتشين", "جميع"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations_found
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
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
        subcategory="inspector_comparison",
        intent=["COMPARE", "TWO", "INSPECTORS"],
        question_en="Compare inspector {inspector1} to {inspector2}",
        question_ar="قارن المفتش {inspector1} بـ {inspector2}",
        variations_en=["Two inspector comparison", "Inspector vs inspector", "Head to head"],
        variations_ar=["مقارنة مفتشين", "مفتش مقابل مفتش"],
        keywords_en=["compare", "inspector", "vs", "to"],
        keywords_ar=["مقارنة", "مفتش", "مقابل"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(DISTINCT e.LocationID) as locations
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE (u.Name LIKE '%{inspector1}%' OR u.Name LIKE '%{inspector2}%')
                  AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
        """,
        parameters={"inspector1": str, "inspector2": str, "year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_INSP_003",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "TOP", "BOTTOM", "INSPECTORS"],
        question_en="Compare top 3 vs bottom 3 inspectors",
        question_ar="قارن أفضل 3 مفتشين بأسوأ 3",
        variations_en=["Best vs worst inspectors", "Top vs bottom performers", "Performance extremes"],
        variations_ar=["الأفضل مقابل الأسوأ", "الأعلى مقابل الأدنى أداءً"],
        keywords_en=["compare", "top", "bottom", "inspectors"],
        keywords_ar=["مقارنة", "أفضل", "أسوأ", "مفتشين"],
        sql="""
            WITH RankedInspectors AS (
                SELECT u.Name as inspector,
                       CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                       COUNT(e.Id) as inspections,
                       ROW_NUMBER() OVER (ORDER BY AVG(e.Score) DESC) as rank_top,
                       ROW_NUMBER() OVER (ORDER BY AVG(e.Score) ASC) as rank_bottom
                FROM [User] u
                JOIN Event e ON e.ReporterID = u.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY u.Id, u.Name
                HAVING COUNT(e.Id) >= 5
            )
            SELECT inspector, avg_score, inspections,
                   CASE WHEN rank_top <= 3 THEN 'Top 3' ELSE 'Bottom 3' END as category
            FROM RankedInspectors
            WHERE rank_top <= 3 OR rank_bottom <= 3
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_004",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTOR", "PRODUCTIVITY"],
        question_en="Compare inspector productivity",
        question_ar="قارن إنتاجية المفتشين",
        variations_en=["Productivity comparison", "Output comparison", "Work volume comparison"],
        variations_ar=["مقارنة الإنتاجية", "مقارنة حجم العمل"],
        keywords_en=["compare", "productivity", "output", "inspectors"],
        keywords_ar=["مقارنة", "إنتاجية", "إخراج", "مفتشين"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as total_inspections,
                   COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)) as work_days,
                   CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)), 0) AS DECIMAL(5,2)) as avg_per_day
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY avg_per_day DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_005",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTOR", "STRICTNESS"],
        question_en="Compare inspector strictness",
        question_ar="قارن صرامة المفتشين",
        variations_en=["Strictness comparison", "Who is strictest?", "Violation rates by inspector"],
        variations_ar=["مقارنة الصرامة", "من الأكثر صرامة؟"],
        keywords_en=["compare", "strictness", "strict", "inspector"],
        keywords_ar=["مقارنة", "صرامة", "صارم", "مفتش"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   COUNT(ev.Id) as violations_found,
                   CAST(COUNT(ev.Id) * 1.0 / NULLIF(COUNT(e.Id), 0) AS DECIMAL(5,2)) as violations_per_inspection
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(e.Id) >= 5
            ORDER BY violations_per_inspection DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_006",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTOR", "CONSISTENCY"],
        question_en="Compare inspector consistency in scoring",
        question_ar="قارن اتساق المفتشين في التقييم",
        variations_en=["Consistency comparison", "Scoring variance", "Inspector stability"],
        variations_ar=["مقارنة الاتساق", "تباين التقييم"],
        keywords_en=["compare", "consistency", "scoring", "variance"],
        keywords_ar=["مقارنة", "اتساق", "تقييم", "تباين"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(STDEV(e.Score) AS DECIMAL(5,2)) as score_std_dev
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(e.Id) >= 5
            ORDER BY score_std_dev ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_007",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "NEW", "EXPERIENCED", "INSPECTORS"],
        question_en="Compare new inspectors vs experienced ones",
        question_ar="قارن المفتشين الجدد بالمخضرمين",
        variations_en=["New vs experienced", "Rookies vs veterans", "Experience comparison"],
        variations_ar=["الجدد مقابل المخضرمين", "مقارنة الخبرة"],
        keywords_en=["compare", "new", "experienced", "inspector"],
        keywords_ar=["مقارنة", "جديد", "خبرة", "مفتش"],
        sql="""
            SELECT 
                CASE 
                    WHEN MIN(e.SubmitionDate) >= DATEADD(month, -6, GETDATE()) THEN 'New (< 6 months)'
                    ELSE 'Experienced (6+ months)'
                END as experience_level,
                COUNT(e.Id) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MIN(e.SubmitionDate) >= DATEADD(month, -6, GETDATE()) THEN 'New (< 6 months)'
                          ELSE 'Experienced (6+ months)' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_008",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTOR", "IMPROVEMENT"],
        question_en="Which inspectors have improved the most?",
        question_ar="أي المفتشين تحسنوا أكثر؟",
        variations_en=["Most improved inspectors", "Inspector improvement", "Performance gains"],
        variations_ar=["المفتشون الأكثر تحسناً", "تحسن المفتشين"],
        keywords_en=["improved", "most", "inspector", "gains"],
        keywords_ar=["تحسن", "أكثر", "مفتش"],
        sql="""
            SELECT u.Name as inspector,
                   CAST(AVG(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN e.Score END) AS DECIMAL(5,2)) as recent_avg,
                   CAST(AVG(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN e.Score END) AS DECIMAL(5,2)) as earlier_avg,
                   CAST(AVG(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN e.Score END) - 
                        AVG(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN e.Score END) AS DECIMAL(5,2)) as improvement
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING AVG(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN e.Score END) IS NOT NULL
               AND AVG(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN e.Score END) IS NOT NULL
            ORDER BY improvement DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="COMP_INSP_009",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTOR", "COVERAGE"],
        question_en="Compare geographic coverage by inspector",
        question_ar="قارن التغطية الجغرافية للمفتشين",
        variations_en=["Coverage comparison", "Area coverage by inspector", "Territory comparison"],
        variations_ar=["مقارنة التغطية", "التغطية الجغرافية"],
        keywords_en=["compare", "coverage", "geographic", "inspector"],
        keywords_ar=["مقارنة", "تغطية", "جغرافي", "مفتش"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(DISTINCT n.Id) as neighborhoods_covered,
                   COUNT(DISTINCT l.Id) as locations_covered,
                   COUNT(e.Id) as total_inspections
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            JOIN Location l ON e.LocationID = l.Id
            JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY neighborhoods_covered DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_INSP_010",
        category=QuestionCategory.COMPARISON,
        subcategory="inspector_comparison",
        intent=["COMPARE", "INSPECTOR", "VIOLATIONS", "TYPES"],
        question_en="Compare violation types found by each inspector",
        question_ar="قارن أنواع المخالفات التي وجدها كل مفتش",
        variations_en=["Violation types by inspector", "What does each inspector find?", "Inspector specialization"],
        variations_ar=["أنواع المخالفات للمفتشين", "ماذا يجد كل مفتش؟"],
        keywords_en=["compare", "violations", "types", "inspector"],
        keywords_ar=["مقارنة", "مخالفات", "أنواع", "مفتش"],
        sql="""
            SELECT u.Name as inspector, vt.Name as violation_type,
                   COUNT(*) as count
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, vt.Id, vt.Name
            ORDER BY u.Name, count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# LOCATION COMPARISON QUESTIONS (10 questions)
# ============================================================================

LOCATION_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_LOC_001",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "LOCATIONS"],
        question_en="Compare all locations by performance",
        question_ar="قارن جميع المواقع حسب الأداء",
        variations_en=["Location comparison", "Compare sites", "All locations compared"],
        variations_ar=["مقارنة المواقع", "قارن المواقع"],
        keywords_en=["compare", "locations", "all", "performance"],
        keywords_ar=["مقارنة", "مواقع", "جميع", "أداء"],
        sql="""
            SELECT l.Name as location,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
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
        subcategory="location_comparison",
        intent=["COMPARE", "NEIGHBORHOODS"],
        question_en="Compare all neighborhoods",
        question_ar="قارن جميع الأحياء",
        variations_en=["Neighborhood comparison", "Compare areas", "All neighborhoods compared"],
        variations_ar=["مقارنة الأحياء", "قارن المناطق"],
        keywords_en=["compare", "neighborhoods", "areas", "all"],
        keywords_ar=["مقارنة", "أحياء", "مناطق", "جميع"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_LOC_003",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "LOCATION", "IMPROVEMENT"],
        question_en="Which locations improved the most?",
        question_ar="أي المواقع تحسنت أكثر؟",
        variations_en=["Most improved locations", "Location improvement", "Sites getting better"],
        variations_ar=["المواقع الأكثر تحسناً", "تحسن المواقع"],
        keywords_en=["improved", "most", "locations", "better"],
        keywords_ar=["تحسن", "أكثر", "مواقع", "أفضل"],
        sql="""
            SELECT TOP 10 l.Name as location,
                   CAST(AVG(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN e.Score END) AS DECIMAL(5,2)) as recent_avg,
                   CAST(AVG(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN e.Score END) AS DECIMAL(5,2)) as earlier_avg,
                   CAST(AVG(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN e.Score END) - 
                        AVG(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN e.Score END) AS DECIMAL(5,2)) as improvement
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING AVG(CASE WHEN MONTH(e.SubmitionDate) > 6 THEN e.Score END) IS NOT NULL
               AND AVG(CASE WHEN MONTH(e.SubmitionDate) <= 6 THEN e.Score END) IS NOT NULL
            ORDER BY improvement DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="COMP_LOC_004",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "TWO", "NEIGHBORHOODS"],
        question_en="Compare neighborhood {neighborhood1} to {neighborhood2}",
        question_ar="قارن حي {neighborhood1} بحي {neighborhood2}",
        variations_en=["Two neighborhood comparison", "Area vs area", "Neighborhood vs neighborhood"],
        variations_ar=["مقارنة حيين", "منطقة مقابل منطقة"],
        keywords_en=["compare", "neighborhood", "vs", "to"],
        keywords_ar=["مقارنة", "حي", "مقابل"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(DISTINCT l.Id) as locations
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE (n.Name LIKE '%{neighborhood1}%' OR n.Name LIKE '%{neighborhood2}%')
                  AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
        """,
        parameters={"neighborhood1": str, "neighborhood2": str, "year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_LOC_005",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "BEST", "WORST", "LOCATIONS"],
        question_en="Compare best and worst performing locations",
        question_ar="قارن أفضل وأسوأ المواقع أداءً",
        variations_en=["Best vs worst locations", "Top vs bottom sites", "Performance extremes"],
        variations_ar=["الأفضل مقابل الأسوأ", "الأعلى مقابل الأدنى"],
        keywords_en=["compare", "best", "worst", "locations"],
        keywords_ar=["مقارنة", "أفضل", "أسوأ", "مواقع"],
        sql="""
            WITH RankedLocations AS (
                SELECT l.Name as location,
                       CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                       COUNT(e.Id) as inspections,
                       ROW_NUMBER() OVER (ORDER BY AVG(e.Score) DESC) as rank_best,
                       ROW_NUMBER() OVER (ORDER BY AVG(e.Score) ASC) as rank_worst
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id, l.Name
                HAVING COUNT(e.Id) >= 2
            )
            SELECT location, avg_score, inspections,
                   CASE WHEN rank_best <= 5 THEN 'Best' ELSE 'Worst' END as category
            FROM RankedLocations
            WHERE rank_best <= 5 OR rank_worst <= 5
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_LOC_006",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "LOCATION", "VIOLATIONS"],
        question_en="Compare violation rates across locations",
        question_ar="قارن معدلات المخالفات عبر المواقع",
        variations_en=["Violation rates comparison", "Location violations", "Sites by violations"],
        variations_ar=["مقارنة معدلات المخالفات", "مخالفات المواقع"],
        keywords_en=["compare", "violations", "rates", "locations"],
        keywords_ar=["مقارنة", "مخالفات", "معدلات", "مواقع"],
        sql="""
            SELECT l.Name as location,
                   COUNT(e.Id) as inspections,
                   COUNT(ev.Id) as violations,
                   CAST(COUNT(ev.Id) * 1.0 / NULLIF(COUNT(e.Id), 0) AS DECIMAL(5,2)) as violations_per_inspection
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(e.Id) >= 2
            ORDER BY violations_per_inspection DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_LOC_007",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "URBAN", "RURAL"],
        question_en="Compare urban vs heritage site performance",
        question_ar="قارن أداء المواقع الحضرية مقابل التراثية",
        variations_en=["Urban vs heritage", "Site type comparison", "Location type performance"],
        variations_ar=["حضري مقابل تراثي", "مقارنة أنواع المواقع"],
        keywords_en=["compare", "urban", "heritage", "site"],
        keywords_ar=["مقارنة", "حضري", "تراثي", "موقع"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(DISTINCT l.Id) as locations
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_LOC_008",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "LOCATION", "FREQUENCY"],
        question_en="Compare inspection frequency across locations",
        question_ar="قارن تكرار الفحص عبر المواقع",
        variations_en=["Inspection frequency comparison", "How often are locations inspected?", "Visit frequency"],
        variations_ar=["مقارنة تكرار الفحص", "كم مرة يتم فحص المواقع؟"],
        keywords_en=["compare", "frequency", "how often", "locations"],
        keywords_ar=["مقارنة", "تكرار", "كم مرة", "مواقع"],
        sql="""
            SELECT l.Name as location,
                   COUNT(e.Id) as inspections,
                   DATEDIFF(day, MIN(e.SubmitionDate), MAX(e.SubmitionDate)) as days_span,
                   CASE WHEN COUNT(e.Id) > 1 THEN 
                        CAST(DATEDIFF(day, MIN(e.SubmitionDate), MAX(e.SubmitionDate)) * 1.0 / 
                             (COUNT(e.Id) - 1) AS DECIMAL(5,1))
                   ELSE NULL END as avg_days_between
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(e.Id) >= 2
            ORDER BY avg_days_between ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_LOC_009",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "NEIGHBORHOOD", "VIOLATIONS"],
        question_en="Compare violation types by neighborhood",
        question_ar="قارن أنواع المخالفات حسب الحي",
        variations_en=["Violations by neighborhood", "Area violation profiles", "Neighborhood issues"],
        variations_ar=["المخالفات حسب الحي", "ملفات مخالفات المنطقة"],
        keywords_en=["compare", "violations", "neighborhood", "types"],
        keywords_ar=["مقارنة", "مخالفات", "حي", "أنواع"],
        sql="""
            SELECT n.Name as neighborhood, vt.Name as violation_type,
                   COUNT(*) as count
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, vt.Id, vt.Name
            ORDER BY n.Name, count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_LOC_010",
        category=QuestionCategory.COMPARISON,
        subcategory="location_comparison",
        intent=["COMPARE", "NEW", "OLD", "LOCATIONS"],
        question_en="Compare newly inspected locations vs established ones",
        question_ar="قارن المواقع المفحوصة حديثاً بالقديمة",
        variations_en=["New vs established locations", "Recent vs long-term sites", "Location tenure comparison"],
        variations_ar=["الجديدة مقابل القديمة", "الحديثة مقابل طويلة الأمد"],
        keywords_en=["compare", "new", "old", "established", "locations"],
        keywords_ar=["مقارنة", "جديد", "قديم", "مواقع"],
        sql="""
            SELECT 
                CASE 
                    WHEN MIN(e.SubmitionDate) >= DATEADD(month, -6, GETDATE()) THEN 'New (< 6 months)'
                    ELSE 'Established (6+ months)'
                END as location_tenure,
                COUNT(e.Id) as inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MIN(e.SubmitionDate) >= DATEADD(month, -6, GETDATE()) THEN 'New (< 6 months)'
                          ELSE 'Established (6+ months)' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# BENCHMARK COMPARISON QUESTIONS (10 questions)
# ============================================================================

BENCHMARK_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_BENCH_001",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "BENCHMARK", "AVERAGE"],
        question_en="How does each location compare to the average?",
        question_ar="كيف يقارن كل موقع بالمتوسط؟",
        variations_en=["Location vs average", "Compared to benchmark", "Above or below average"],
        variations_ar=["الموقع مقابل المتوسط", "مقارنة بالمعيار"],
        keywords_en=["compare", "benchmark", "average", "location"],
        keywords_ar=["مقارنة", "معيار", "متوسط", "موقع"],
        sql="""
            WITH OverallAvg AS (
                SELECT CAST(AVG(Score) AS DECIMAL(5,2)) as overall_avg FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            )
            SELECT l.Name as location,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   (SELECT overall_avg FROM OverallAvg) as benchmark,
                   CAST(AVG(e.Score) - (SELECT overall_avg FROM OverallAvg) AS DECIMAL(5,2)) as diff_from_avg
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            ORDER BY diff_from_avg DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_BENCH_002",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "ABOVE", "BELOW", "TARGET"],
        question_en="How many locations are above/below target?",
        question_ar="كم عدد المواقع فوق/تحت الهدف؟",
        variations_en=["Above vs below target", "Target comparison", "Meeting targets"],
        variations_ar=["فوق مقابل تحت الهدف", "مقارنة الهدف"],
        keywords_en=["compare", "above", "below", "target"],
        keywords_ar=["مقارنة", "فوق", "تحت", "هدف"],
        sql="""
            SELECT 
                CASE WHEN AVG(e.Score) >= {target} THEN 'Above Target' ELSE 'Below Target' END as status,
                COUNT(DISTINCT l.Id) as location_count
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id
        """,
        parameters={"year": int, "target": int},
        default_values={"year": 2024, "target": 80},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_BENCH_003",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "INSPECTOR", "AVERAGE"],
        question_en="How does each inspector compare to the average?",
        question_ar="كيف يقارن كل مفتش بالمتوسط؟",
        variations_en=["Inspector vs average", "Inspector benchmark", "Above or below average inspector"],
        variations_ar=["المفتش مقابل المتوسط", "معيار المفتش"],
        keywords_en=["compare", "inspector", "average", "benchmark"],
        keywords_ar=["مقارنة", "مفتش", "متوسط", "معيار"],
        sql="""
            WITH OverallAvg AS (
                SELECT CAST(AVG(Score) AS DECIMAL(5,2)) as overall_avg FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            )
            SELECT u.Name as inspector,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   (SELECT overall_avg FROM OverallAvg) as benchmark,
                   CAST(AVG(e.Score) - (SELECT overall_avg FROM OverallAvg) AS DECIMAL(5,2)) as diff_from_avg
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY diff_from_avg DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_BENCH_004",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "ACTUAL", "TARGET"],
        question_en="Compare actual performance vs target",
        question_ar="قارن الأداء الفعلي بالهدف",
        variations_en=["Actual vs target", "Performance vs goal", "Target attainment"],
        variations_ar=["الفعلي مقابل الهدف", "الأداء مقابل الهدف"],
        keywords_en=["compare", "actual", "target", "performance"],
        keywords_ar=["مقارنة", "فعلي", "هدف", "أداء"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as actual_avg,
                {target} as target,
                CAST(AVG(e.Score) - {target} AS DECIMAL(5,2)) as variance
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int, "target": int},
        default_values={"year": 2024, "target": 80},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_BENCH_005",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "PERCENTILE"],
        question_en="What percentile is each location in?",
        question_ar="ما هي النسبة المئوية لكل موقع؟",
        variations_en=["Location percentiles", "Performance ranking percentile", "Where does each location stand?"],
        variations_ar=["النسب المئوية للمواقع", "تصنيف الأداء"],
        keywords_en=["percentile", "ranking", "where", "location"],
        keywords_ar=["نسبة مئوية", "تصنيف", "أين", "موقع"],
        sql="""
            SELECT l.Name as location,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(PERCENT_RANK() OVER (ORDER BY AVG(e.Score)) * 100 AS DECIMAL(5,1)) as percentile
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(e.Id) >= 2
            ORDER BY percentile DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="COMP_BENCH_006",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "NEIGHBORHOOD", "BENCHMARK"],
        question_en="How does each neighborhood compare to the overall benchmark?",
        question_ar="كيف يقارن كل حي بالمعيار العام؟",
        variations_en=["Neighborhood vs benchmark", "Area benchmarking", "Neighborhood standing"],
        variations_ar=["الحي مقابل المعيار", "قياس أداء المنطقة"],
        keywords_en=["compare", "neighborhood", "benchmark", "overall"],
        keywords_ar=["مقارنة", "حي", "معيار", "عام"],
        sql="""
            WITH OverallAvg AS (
                SELECT CAST(AVG(Score) AS DECIMAL(5,2)) as overall_avg FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            )
            SELECT n.Name as neighborhood,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   (SELECT overall_avg FROM OverallAvg) as benchmark,
                   CAST(AVG(e.Score) - (SELECT overall_avg FROM OverallAvg) AS DECIMAL(5,2)) as diff_from_benchmark
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY diff_from_benchmark DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_BENCH_007",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "IMPROVEMENT", "NEEDED"],
        question_en="How much improvement does each location need?",
        question_ar="كم التحسن المطلوب لكل موقع؟",
        variations_en=["Improvement needed", "Gap to target", "Points needed"],
        variations_ar=["التحسن المطلوب", "الفجوة للهدف"],
        keywords_en=["improvement", "needed", "gap", "location"],
        keywords_ar=["تحسن", "مطلوب", "فجوة", "موقع"],
        sql="""
            SELECT l.Name as location,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as current_avg,
                   {target} as target,
                   CASE WHEN AVG(e.Score) >= {target} THEN 0 
                        ELSE CAST({target} - AVG(e.Score) AS DECIMAL(5,2)) END as points_needed
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING AVG(e.Score) < {target}
            ORDER BY points_needed DESC
        """,
        parameters={"year": int, "target": int},
        default_values={"year": 2024, "target": 80},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_BENCH_008",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "LAST", "YEAR", "BENCHMARK"],
        question_en="Compare this year's performance to last year's benchmark",
        question_ar="قارن أداء هذا العام بمعيار العام الماضي",
        variations_en=["This year vs last year benchmark", "YoY benchmark", "Historical benchmark comparison"],
        variations_ar=["هذا العام مقابل معيار العام الماضي", "مقارنة معيار سنوية"],
        keywords_en=["compare", "this year", "last year", "benchmark"],
        keywords_ar=["مقارنة", "هذا العام", "العام الماضي", "معيار"],
        sql="""
            SELECT 
                YEAR(e.SubmitionDate) as year,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(e.Id) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) IN ({year}, {year}-1)
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_BENCH_009",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["COMPARE", "COMPLIANCE", "RATE"],
        question_en="Compare compliance rates across entities",
        question_ar="قارن معدلات الامتثال عبر الكيانات",
        variations_en=["Compliance rate comparison", "Who is most compliant?", "Compliance benchmarking"],
        variations_ar=["مقارنة معدلات الامتثال", "من الأكثر امتثالاً؟"],
        keywords_en=["compare", "compliance", "rate", "entities"],
        keywords_ar=["مقارنة", "امتثال", "معدل", "كيانات"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) as compliant,
                   CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(e.Id), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY compliance_rate DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_BENCH_010",
        category=QuestionCategory.COMPARISON,
        subcategory="benchmark",
        intent=["RANK", "OVERALL"],
        question_en="Rank all entities by overall performance",
        question_ar="رتب جميع الكيانات حسب الأداء العام",
        variations_en=["Overall ranking", "Performance leaderboard", "All entities ranked"],
        variations_ar=["الترتيب العام", "لوحة المتصدرين"],
        keywords_en=["rank", "overall", "all", "performance"],
        keywords_ar=["ترتيب", "عام", "جميع", "أداء"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   RANK() OVER (ORDER BY AVG(e.Score) DESC) as overall_rank
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY overall_rank
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# VIOLATION COMPARISON QUESTIONS (10 questions)
# ============================================================================

VIOLATION_COMPARISON_QUESTIONS = [
    QuestionTemplate(
        id="COMP_VIOL_001",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "TYPES"],
        question_en="Compare all violation types by frequency",
        question_ar="قارن جميع أنواع المخالفات بالتكرار",
        variations_en=["Violation type comparison", "Compare violations", "Which violations are most common?"],
        variations_ar=["مقارنة أنواع المخالفات", "قارن المخالفات"],
        keywords_en=["compare", "violation", "types", "frequency"],
        keywords_ar=["مقارنة", "مخالفة", "أنواع", "تكرار"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(*) as count,
                   RANK() OVER (ORDER BY COUNT(*) DESC) as rank
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            ORDER BY count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_VIOL_002",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "CATEGORIES"],
        question_en="Compare violation categories",
        question_ar="قارن فئات المخالفات",
        variations_en=["Category comparison", "Compare violation categories", "Categories by count"],
        variations_ar=["مقارنة الفئات", "قارن فئات المخالفات"],
        keywords_en=["compare", "violation", "categories"],
        keywords_ar=["مقارنة", "مخالفة", "فئات"],
        sql="""
            SELECT vc.Name as category,
                   COUNT(ev.Id) as violations,
                   CAST(COUNT(ev.Id) * 100.0 / SUM(COUNT(ev.Id)) OVER () AS DECIMAL(5,2)) as percentage
            FROM ViolationCategory vc
            JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY violations DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_VIOL_003",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "TREND"],
        question_en="Compare violation trends month by month",
        question_ar="قارن اتجاهات المخالفات شهر بشهر",
        variations_en=["Violation trend comparison", "Monthly violation trends", "Violations over time"],
        variations_ar=["مقارنة اتجاهات المخالفات", "اتجاهات المخالفات الشهرية"],
        keywords_en=["compare", "violation", "trend", "monthly"],
        keywords_ar=["مقارنة", "مخالفة", "اتجاه", "شهري"],
        sql="""
            SELECT FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
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
        id="COMP_VIOL_004",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "THIS", "LAST", "YEAR"],
        question_en="Compare violations this year vs last year",
        question_ar="قارن المخالفات هذا العام بالعام الماضي",
        variations_en=["Year over year violations", "This year vs last year violations", "Violation YoY"],
        variations_ar=["المخالفات سنوية", "هذا العام مقابل العام الماضي"],
        keywords_en=["compare", "violations", "this year", "last year"],
        keywords_ar=["مقارنة", "مخالفات", "هذا العام", "العام الماضي"],
        sql="""
            SELECT YEAR(e.SubmitionDate) as year,
                   COUNT(ev.Id) as violations,
                   COUNT(DISTINCT vt.Id) as unique_types
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            LEFT JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) IN ({year}, {year}-1)
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_VIOL_005",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "SEVERITY"],
        question_en="Compare violation severity distribution",
        question_ar="قارن توزيع شدة المخالفات",
        variations_en=["Severity comparison", "How severe are violations?", "Violation severity breakdown"],
        variations_ar=["مقارنة الشدة", "ما مدى شدة المخالفات؟"],
        keywords_en=["compare", "severity", "violation", "distribution"],
        keywords_ar=["مقارنة", "شدة", "مخالفة", "توزيع"],
        sql="""
            SELECT 
                CASE 
                    WHEN ev.Value >= 100 THEN 'High'
                    WHEN ev.Value >= 50 THEN 'Medium'
                    ELSE 'Low'
                END as severity,
                COUNT(*) as count,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS DECIMAL(5,2)) as percentage
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN ev.Value >= 100 THEN 'High' WHEN ev.Value >= 50 THEN 'Medium' ELSE 'Low' END
            ORDER BY count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="COMP_VIOL_006",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "QUARTER"],
        question_en="Compare violations by quarter",
        question_ar="قارن المخالفات حسب الربع",
        variations_en=["Quarterly violations", "Q1 vs Q2 vs Q3 vs Q4 violations", "Violations per quarter"],
        variations_ar=["المخالفات الربعية", "مخالفات كل ربع"],
        keywords_en=["compare", "violations", "quarter", "quarterly"],
        keywords_ar=["مقارنة", "مخالفات", "ربع", "ربعي"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) <= 3 THEN 'Q1'
                    WHEN MONTH(e.SubmitionDate) <= 6 THEN 'Q2'
                    WHEN MONTH(e.SubmitionDate) <= 9 THEN 'Q3'
                    ELSE 'Q4'
                END as quarter,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) <= 3 THEN 'Q1'
                          WHEN MONTH(e.SubmitionDate) <= 6 THEN 'Q2'
                          WHEN MONTH(e.SubmitionDate) <= 9 THEN 'Q3'
                          ELSE 'Q4' END
            ORDER BY quarter
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_VIOL_007",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "LOCATION"],
        question_en="Compare violations per location",
        question_ar="قارن المخالفات لكل موقع",
        variations_en=["Violations by location", "Which locations have most violations?", "Location violation rates"],
        variations_ar=["المخالفات حسب الموقع", "أي المواقع لديها أكثر مخالفات؟"],
        keywords_en=["compare", "violations", "location", "per"],
        keywords_ar=["مقارنة", "مخالفات", "موقع", "لكل"],
        sql="""
            SELECT TOP 15 l.Name as location,
                   COUNT(ev.Id) as violations,
                   COUNT(e.Id) as inspections,
                   CAST(COUNT(ev.Id) * 1.0 / NULLIF(COUNT(e.Id), 0) AS DECIMAL(5,2)) as violations_per_inspection
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            ORDER BY violations DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_VIOL_008",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "NEIGHBORHOOD"],
        question_en="Compare violations per neighborhood",
        question_ar="قارن المخالفات لكل حي",
        variations_en=["Violations by neighborhood", "Which areas have most violations?", "Neighborhood violation comparison"],
        variations_ar=["المخالفات حسب الحي", "أي المناطق لديها أكثر مخالفات؟"],
        keywords_en=["compare", "violations", "neighborhood", "area"],
        keywords_ar=["مقارنة", "مخالفات", "حي", "منطقة"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(ev.Id) as violations,
                   COUNT(e.Id) as inspections,
                   CAST(COUNT(ev.Id) * 1.0 / NULLIF(COUNT(e.Id), 0) AS DECIMAL(5,2)) as violations_per_inspection
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY violations DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="COMP_VIOL_009",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "NEW", "REPEAT", "VIOLATIONS"],
        question_en="Compare new vs repeat violations",
        question_ar="قارن المخالفات الجديدة بالمتكررة",
        variations_en=["New vs repeat violations", "First time vs recurring", "Violation recurrence"],
        variations_ar=["الجديدة مقابل المتكررة", "للمرة الأولى مقابل المتكررة"],
        keywords_en=["compare", "new", "repeat", "violations"],
        keywords_ar=["مقارنة", "جديد", "متكرر", "مخالفات"],
        sql="""
            WITH ViolationHistory AS (
                SELECT ev.*, e.LocationID,
                       ROW_NUMBER() OVER (PARTITION BY e.LocationID, ev.ViolationTypeId ORDER BY e.SubmitionDate) as occurrence_num
                FROM EventViolation ev
                JOIN Event e ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT 
                CASE WHEN occurrence_num = 1 THEN 'New' ELSE 'Repeat' END as violation_type,
                COUNT(*) as count
            FROM ViolationHistory
            GROUP BY CASE WHEN occurrence_num = 1 THEN 'New' ELSE 'Repeat' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="COMP_VIOL_010",
        category=QuestionCategory.COMPARISON,
        subcategory="violation_comparison",
        intent=["COMPARE", "VIOLATION", "VALUE"],
        question_en="Compare violation values by type",
        question_ar="قارن قيم المخالفات حسب النوع",
        variations_en=["Violation values comparison", "Impact by type", "Violation cost comparison"],
        variations_ar=["مقارنة قيم المخالفات", "التأثير حسب النوع"],
        keywords_en=["compare", "violation", "value", "type"],
        keywords_ar=["مقارنة", "مخالفة", "قيمة", "نوع"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(*) as count,
                   SUM(ev.Value) as total_value,
                   CAST(AVG(ev.Value) AS DECIMAL(10,2)) as avg_value
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            ORDER BY total_value DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]


# ============================================================================
# REGISTER ALL EXTENDED COMPARISON QUESTIONS
# ============================================================================

ALL_EXTENDED_COMPARISON_QUESTIONS = (
    TIME_COMPARISON_QUESTIONS +
    INSPECTOR_COMPARISON_QUESTIONS +
    LOCATION_COMPARISON_QUESTIONS +
    BENCHMARK_COMPARISON_QUESTIONS +
    VIOLATION_COMPARISON_QUESTIONS
)

# Register all questions
registry.register_many(ALL_EXTENDED_COMPARISON_QUESTIONS)

print(f"Extended Comparison Questions loaded: {len(ALL_EXTENDED_COMPARISON_QUESTIONS)} templates")
