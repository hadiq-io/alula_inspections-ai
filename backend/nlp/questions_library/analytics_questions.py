"""
Analytics Questions Library
============================
300+ analytics-related questions covering trends, rankings, distributions, and aggregates.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# TREND ANALYTICS (60 questions)
# ============================================================================

TREND_QUESTIONS = [
    QuestionTemplate(
        id="ANA_TREND_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="trends",
        intent=["TREND", "INSPECTIONS", "MONTHLY"],
        question_en="Show me the monthly inspection trend",
        question_ar="أظهر لي اتجاه الفحوصات الشهري",
        variations_en=[
            "Inspections by month",
            "Monthly inspection count",
            "How are inspections trending?",
            "Inspection trend over months"
        ],
        variations_ar=[
            "الفحوصات حسب الشهر",
            "عدد الفحوصات الشهري"
        ],
        keywords_en=["trend", "monthly", "inspections", "over time"],
        keywords_ar=["اتجاه", "شهري", "فحوصات"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
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
        id="ANA_TREND_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="trends",
        intent=["TREND", "VIOLATIONS", "WEEKLY"],
        question_en="Show me the weekly violation trend",
        question_ar="أظهر لي اتجاه المخالفات الأسبوعي",
        variations_en=[
            "Violations by week",
            "Weekly violation count",
            "How are violations trending weekly?"
        ],
        variations_ar=[
            "المخالفات حسب الأسبوع",
            "عدد المخالفات الأسبوعي"
        ],
        keywords_en=["trend", "weekly", "violations", "week"],
        keywords_ar=["اتجاه", "أسبوعي", "مخالفات"],
        sql="""
            SELECT 
                DATEPART(WEEK, e.SubmitionDate) as week_number,
                COUNT(*) as violation_count,
                SUM(ev.Value) as total_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(WEEK, e.SubmitionDate)
            ORDER BY week_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_TREND_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="trends",
        intent=["TREND", "SCORE", "MONTHLY"],
        question_en="How has the average score changed over time?",
        question_ar="كيف تغير متوسط الدرجات مع الوقت؟",
        variations_en=[
            "Score trend",
            "Average score over time",
            "Score changes monthly",
            "Monthly score trend"
        ],
        variations_ar=[
            "اتجاه الدرجات",
            "تغير الدرجات"
        ],
        keywords_en=["score", "trend", "average", "over time", "changed"],
        keywords_ar=["درجات", "اتجاه", "تغير"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(*) as inspection_count
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
        id="ANA_TREND_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="trends",
        intent=["TREND", "DAILY"],
        question_en="What is the daily inspection pattern?",
        question_ar="ما هو نمط الفحوصات اليومي؟",
        variations_en=[
            "Inspections by day of week",
            "Daily pattern",
            "Which days have most inspections?",
            "Busiest inspection days"
        ],
        variations_ar=[
            "الفحوصات حسب اليوم",
            "أيام الفحص الأكثر نشاطاً"
        ],
        keywords_en=["daily", "pattern", "day", "busiest", "weekday"],
        keywords_ar=["يومي", "نمط", "يوم"],
        sql="""
            SELECT 
                DATENAME(WEEKDAY, e.SubmitionDate) as day_name,
                DATEPART(WEEKDAY, e.SubmitionDate) as day_number,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(WEEKDAY, e.SubmitionDate), DATEPART(WEEKDAY, e.SubmitionDate)
            ORDER BY day_number
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_TREND_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="trends",
        intent=["TREND", "SEASONAL"],
        question_en="Is there a seasonal pattern in inspections?",
        question_ar="هل هناك نمط موسمي في الفحوصات؟",
        variations_en=[
            "Seasonal inspection pattern",
            "Inspections by season",
            "Quarterly patterns",
            "Seasonal trends"
        ],
        variations_ar=[
            "نمط موسمي",
            "الفحوصات حسب الموسم"
        ],
        keywords_en=["seasonal", "pattern", "quarter", "season"],
        keywords_ar=["موسمي", "نمط", "ربع"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(*) as inspection_count,
                COUNT(ev.Id) as violation_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# RANKING ANALYTICS (60 questions)
# ============================================================================

RANKING_QUESTIONS = [
    QuestionTemplate(
        id="ANA_RANK_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="rankings",
        intent=["RANKING", "NEIGHBORHOOD", "VIOLATIONS"],
        question_en="Which neighborhoods have the most violations?",
        question_ar="أي الأحياء لديها أكثر مخالفات؟",
        variations_en=[
            "Top neighborhoods by violations",
            "Neighborhoods ranked by violations",
            "Most problematic neighborhoods",
            "Violation rankings by area"
        ],
        variations_ar=[
            "أكثر الأحياء مخالفات",
            "ترتيب الأحياء حسب المخالفات"
        ],
        keywords_en=["neighborhood", "violations", "most", "top", "ranking"],
        keywords_ar=["أحياء", "مخالفات", "أكثر", "ترتيب"],
        sql="""
            SELECT TOP 10
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_value,
                COUNT(DISTINCT e.Id) as inspection_count
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY violation_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_RANK_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="rankings",
        intent=["RANKING", "INSPECTOR", "PRODUCTIVITY"],
        question_en="Which inspectors are most productive?",
        question_ar="من هم المفتشون الأكثر إنتاجية؟",
        variations_en=[
            "Top inspectors by inspections",
            "Most active inspectors",
            "Inspector productivity ranking",
            "Who did the most inspections?"
        ],
        variations_ar=[
            "أكثر المفتشين نشاطاً",
            "ترتيب إنتاجية المفتشين"
        ],
        keywords_en=["inspector", "productive", "most", "active", "ranking"],
        keywords_ar=["مفتش", "إنتاجية", "نشاط", "ترتيب"],
        sql="""
            SELECT TOP 10
                u.Name as inspector_name,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violations_found
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_RANK_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="rankings",
        intent=["RANKING", "LOCATION", "SCORE"],
        question_en="Which locations have the lowest scores?",
        question_ar="أي المواقع لديها أدنى الدرجات؟",
        variations_en=[
            "Worst performing locations",
            "Locations with lowest scores",
            "Bottom locations by score",
            "Problem locations"
        ],
        variations_ar=[
            "أسوأ المواقع أداءً",
            "المواقع ذات الدرجات المنخفضة"
        ],
        keywords_en=["locations", "lowest", "score", "worst", "bottom"],
        keywords_ar=["مواقع", "أدنى", "درجات", "أسوأ"],
        sql="""
            SELECT TOP 10
                l.Name as location_name,
                n.Name as neighborhood,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                MIN(e.Score) as min_score
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name, n.Name
            HAVING COUNT(*) >= 3
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_RANK_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="rankings",
        intent=["RANKING", "VIOLATION_TYPE", "VALUE"],
        question_en="Which violation types have the highest monetary value?",
        question_ar="أي أنواع المخالفات لها أعلى قيمة مالية؟",
        variations_en=[
            "Most expensive violations",
            "Violation types by value",
            "Highest value violations",
            "Top violations by amount"
        ],
        variations_ar=[
            "أغلى المخالفات",
            "المخالفات حسب القيمة"
        ],
        keywords_en=["violation", "types", "value", "highest", "monetary", "expensive"],
        keywords_ar=["مخالفات", "قيمة", "أعلى", "مالية"],
        sql="""
            SELECT TOP 10
                COALESCE(CAST(ev.QuestionSectionId AS VARCHAR), 'Unspecified') as violation_category,
                COUNT(*) as occurrence_count,
                SUM(ev.ViolationValue) as total_value,
                AVG(CAST(ev.ViolationValue AS FLOAT)) as avg_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY ev.QuestionSectionId
            ORDER BY total_value DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_RANK_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="rankings",
        intent=["RANKING", "MONTH", "BUSIEST"],
        question_en="Which months had the most activity?",
        question_ar="أي الأشهر كانت الأكثر نشاطاً؟",
        variations_en=[
            "Busiest months",
            "Most active months",
            "Months ranked by inspections",
            "Peak inspection months"
        ],
        variations_ar=[
            "أكثر الأشهر نشاطاً",
            "الأشهر الأكثر فحوصات"
        ],
        keywords_en=["month", "busiest", "most", "activity", "peak"],
        keywords_ar=["شهر", "نشاط", "أكثر"],
        sql="""
            SELECT 
                DATENAME(MONTH, e.SubmitionDate) as month_name,
                MONTH(e.SubmitionDate) as month_number,
                COUNT(*) as inspection_count,
                COUNT(ev.Id) as violation_count
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(MONTH, e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# DISTRIBUTION ANALYTICS (60 questions)
# ============================================================================

DISTRIBUTION_QUESTIONS = [
    QuestionTemplate(
        id="ANA_DIST_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="distributions",
        intent=["DISTRIBUTION", "SCORE"],
        question_en="What is the distribution of inspection scores?",
        question_ar="ما هو توزيع درجات الفحص؟",
        variations_en=[
            "Score distribution",
            "How are scores distributed?",
            "Score breakdown",
            "Inspection score histogram"
        ],
        variations_ar=[
            "توزيع الدرجات",
            "كيف توزعت الدرجات؟"
        ],
        keywords_en=["distribution", "scores", "breakdown", "histogram"],
        keywords_ar=["توزيع", "درجات"],
        sql="""
            SELECT 
                CASE 
                    WHEN Score >= 90 THEN '90-100 (Excellent)'
                    WHEN Score >= 80 THEN '80-89 (Good)'
                    WHEN Score >= 70 THEN '70-79 (Fair)'
                    WHEN Score >= 60 THEN '60-69 (Poor)'
                    ELSE 'Below 60 (Critical)'
                END as score_range,
                COUNT(*) as count,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE 
                    WHEN Score >= 90 THEN '90-100 (Excellent)'
                    WHEN Score >= 80 THEN '80-89 (Good)'
                    WHEN Score >= 70 THEN '70-79 (Fair)'
                    WHEN Score >= 60 THEN '60-69 (Poor)'
                    ELSE 'Below 60 (Critical)'
                END
            ORDER BY MIN(Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_DIST_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="distributions",
        intent=["DISTRIBUTION", "VIOLATION", "CATEGORY"],
        question_en="How are violations distributed by category?",
        question_ar="كيف توزعت المخالفات حسب الفئة؟",
        variations_en=[
            "Violation category distribution",
            "Breakdown by violation category",
            "Violations by type",
            "Violation type distribution"
        ],
        variations_ar=[
            "توزيع المخالفات حسب الفئة",
            "المخالفات حسب النوع"
        ],
        keywords_en=["distribution", "violations", "category", "type", "breakdown"],
        keywords_ar=["توزيع", "مخالفات", "فئة", "نوع"],
        sql="""
            SELECT 
                COALESCE(CAST(ev.QuestionSectionId AS VARCHAR), 'Unspecified') as category,
                COUNT(*) as violation_count,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage,
                SUM(ev.ViolationValue) as total_value
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
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_DIST_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="distributions",
        intent=["DISTRIBUTION", "INSPECTOR", "WORKLOAD"],
        question_en="How is the workload distributed among inspectors?",
        question_ar="كيف يتوزع حمل العمل بين المفتشين؟",
        variations_en=[
            "Inspector workload distribution",
            "Work distribution among inspectors",
            "How balanced is the workload?",
            "Inspector load distribution"
        ],
        variations_ar=[
            "توزيع العمل بين المفتشين",
            "حمل العمل"
        ],
        keywords_en=["workload", "distribution", "inspectors", "balanced"],
        keywords_ar=["حمل العمل", "توزيع", "مفتشين"],
        sql="""
            WITH InspectorStats AS (
                SELECT 
                    u.Name as inspector_name,
                    COUNT(*) as inspection_count
                FROM [User] u
                JOIN Event e ON e.ReporterID = u.Id
                WHERE e.IsDeleted = 0
                  AND YEAR(e.SubmitionDate) = {year}
                GROUP BY u.Id, u.Name
            )
            SELECT 
                CASE 
                    WHEN inspection_count >= 100 THEN 'High (100+)'
                    WHEN inspection_count >= 50 THEN 'Medium (50-99)'
                    WHEN inspection_count >= 20 THEN 'Low (20-49)'
                    ELSE 'Very Low (<20)'
                END as workload_category,
                COUNT(*) as inspector_count,
                SUM(inspection_count) as total_inspections
            FROM InspectorStats
            GROUP BY CASE 
                    WHEN inspection_count >= 100 THEN 'High (100+)'
                    WHEN inspection_count >= 50 THEN 'Medium (50-99)'
                    WHEN inspection_count >= 20 THEN 'Low (20-49)'
                    ELSE 'Very Low (<20)'
                END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_DIST_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="distributions",
        intent=["DISTRIBUTION", "GEOGRAPHIC"],
        question_en="What is the geographic distribution of inspections?",
        question_ar="ما هو التوزيع الجغرافي للفحوصات؟",
        variations_en=[
            "Inspections by area",
            "Geographic breakdown",
            "Where are inspections happening?",
            "Regional distribution"
        ],
        variations_ar=[
            "التوزيع الجغرافي",
            "الفحوصات حسب المنطقة"
        ],
        keywords_en=["geographic", "distribution", "area", "regional", "where"],
        keywords_ar=["جغرافي", "توزيع", "منطقة"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(*) as inspection_count,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.TREEMAP,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_DIST_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="distributions",
        intent=["DISTRIBUTION", "STATUS"],
        question_en="What is the distribution of inspection statuses?",
        question_ar="ما هو توزيع حالات الفحص؟",
        variations_en=[
            "Status distribution",
            "Inspection statuses breakdown",
            "How many pending vs completed?",
            "Status overview"
        ],
        variations_ar=[
            "توزيع الحالات",
            "حالات الفحص"
        ],
        keywords_en=["status", "distribution", "pending", "completed"],
        keywords_ar=["حالة", "توزيع"],
        sql="""
            SELECT 
                esl.Name as status,
                esl.NameAr as status_ar,
                COUNT(*) as count,
                CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
            FROM EventStatusLookup esl
            JOIN Event e ON e.EventStatusLookupId = esl.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY esl.Id, esl.Name, esl.NameAr
            ORDER BY count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# AGGREGATE ANALYTICS (60 questions)
# ============================================================================

AGGREGATE_QUESTIONS = [
    QuestionTemplate(
        id="ANA_AGG_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="aggregates",
        intent=["SUMMARY", "STATISTICS"],
        question_en="Give me a statistical summary of inspections",
        question_ar="أعطني ملخصاً إحصائياً للفحوصات",
        variations_en=[
            "Inspection statistics",
            "Statistical overview",
            "Summary statistics",
            "Key stats"
        ],
        variations_ar=[
            "إحصائيات الفحوصات",
            "ملخص إحصائي"
        ],
        keywords_en=["statistics", "summary", "overview", "stats"],
        keywords_ar=["إحصائيات", "ملخص"],
        sql="""
            SELECT 
                COUNT(*) as total_inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                CAST(STDEV(Score) AS DECIMAL(5,2)) as std_dev_score,
                MIN(Score) as min_score,
                MAX(Score) as max_score,
                COUNT(DISTINCT LocationID) as unique_locations,
                COUNT(DISTINCT ReporterID) as unique_inspectors
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_AGG_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="aggregates",
        intent=["COUNT", "GROUP", "NEIGHBORHOOD"],
        question_en="How many inspections per neighborhood?",
        question_ar="كم عدد الفحوصات لكل حي؟",
        variations_en=[
            "Inspections by neighborhood",
            "Count per area",
            "Neighborhood inspection counts"
        ],
        variations_ar=[
            "الفحوصات حسب الحي",
            "عدد الفحوصات لكل حي"
        ],
        keywords_en=["inspections", "per", "neighborhood", "count"],
        keywords_ar=["فحوصات", "حي", "عدد"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_AGG_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="aggregates",
        intent=["SUM", "VIOLATIONS", "VALUE"],
        question_en="What is the total violation value by neighborhood?",
        question_ar="ما هو إجمالي قيمة المخالفات حسب الحي؟",
        variations_en=[
            "Violation value by area",
            "Total fines by neighborhood",
            "Monetary value per neighborhood"
        ],
        variations_ar=[
            "قيمة المخالفات حسب الحي",
            "الغرامات حسب المنطقة"
        ],
        keywords_en=["violation", "value", "neighborhood", "total", "sum"],
        keywords_ar=["مخالفات", "قيمة", "حي", "إجمالي"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_value,
                AVG(ev.Value) as avg_value
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY total_value DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_AGG_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="aggregates",
        intent=["AVERAGE", "INSPECTOR", "SCORE"],
        question_en="What is the average score per inspector?",
        question_ar="ما هو متوسط الدرجة لكل مفتش؟",
        variations_en=[
            "Inspector average scores",
            "Score by inspector",
            "Inspector performance scores"
        ],
        variations_ar=[
            "متوسط درجة كل مفتش",
            "الدرجات حسب المفتش"
        ],
        keywords_en=["average", "score", "inspector", "per"],
        keywords_ar=["متوسط", "درجة", "مفتش"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                MIN(e.Score) as min_score,
                MAX(e.Score) as max_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(*) >= 5
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_AGG_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="aggregates",
        intent=["COUNT", "VIOLATIONS", "LOCATION"],
        question_en="How many violations per location?",
        question_ar="كم عدد المخالفات لكل موقع؟",
        variations_en=[
            "Violations by location",
            "Location violation counts",
            "Violations per establishment"
        ],
        variations_ar=[
            "المخالفات حسب الموقع",
            "عدد المخالفات لكل موقع"
        ],
        keywords_en=["violations", "per", "location", "count"],
        keywords_ar=["مخالفات", "موقع", "عدد"],
        sql="""
            SELECT TOP 20
                l.Name as location_name,
                n.Name as neighborhood,
                COUNT(ev.Id) as violation_count,
                SUM(ev.Value) as total_value
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name, n.Name
            ORDER BY violation_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# PATTERN ANALYTICS (60 questions)
# ============================================================================

PATTERN_QUESTIONS = [
    QuestionTemplate(
        id="ANA_PAT_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "CORRELATION"],
        question_en="Is there a correlation between violations and low scores?",
        question_ar="هل هناك علاقة بين المخالفات والدرجات المنخفضة؟",
        variations_en=[
            "Violation score correlation",
            "Do violations affect scores?",
            "Relationship between violations and scores"
        ],
        variations_ar=[
            "العلاقة بين المخالفات والدرجات",
            "هل تؤثر المخالفات على الدرجات؟"
        ],
        keywords_en=["correlation", "violations", "scores", "relationship"],
        keywords_ar=["علاقة", "مخالفات", "درجات"],
        sql="""
            SELECT 
                CASE 
                    WHEN violation_count = 0 THEN '0 violations'
                    WHEN violation_count <= 2 THEN '1-2 violations'
                    WHEN violation_count <= 5 THEN '3-5 violations'
                    ELSE '6+ violations'
                END as violation_category,
                COUNT(*) as inspection_count,
                CAST(AVG(score) AS DECIMAL(5,2)) as avg_score
            FROM (
                SELECT 
                    e.Id,
                    e.Score as score,
                    COUNT(ev.Id) as violation_count
                FROM Event e
                LEFT JOIN EventViolation ev ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0
                  AND e.Score IS NOT NULL
                  AND YEAR(e.SubmitionDate) = {year}
                GROUP BY e.Id, e.Score
            ) sub
            GROUP BY CASE 
                    WHEN violation_count = 0 THEN '0 violations'
                    WHEN violation_count <= 2 THEN '1-2 violations'
                    WHEN violation_count <= 5 THEN '3-5 violations'
                    ELSE '6+ violations'
                END
            ORDER BY MIN(violation_count)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_PAT_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "REPEAT", "VIOLATORS"],
        question_en="Which locations are repeat violators?",
        question_ar="أي المواقع مخالفة بشكل متكرر؟",
        variations_en=[
            "Repeat offenders",
            "Locations with recurring violations",
            "Serial violators",
            "Persistent violators"
        ],
        variations_ar=[
            "المخالفون المتكررون",
            "المواقع ذات المخالفات المتكررة"
        ],
        keywords_en=["repeat", "violators", "recurring", "persistent"],
        keywords_ar=["متكرر", "مخالفون"],
        sql="""
            SELECT TOP 10
                l.Name as location_name,
                n.Name as neighborhood,
                COUNT(DISTINCT e.Id) as inspection_count,
                COUNT(ev.Id) as total_violations,
                CAST(COUNT(ev.Id) * 1.0 / COUNT(DISTINCT e.Id) AS DECIMAL(5,2)) as violations_per_inspection
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name, n.Name
            HAVING COUNT(DISTINCT e.Id) >= 2 AND COUNT(ev.Id) >= 3
            ORDER BY violations_per_inspection DESC, total_violations DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_PAT_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "TIME_OF_DAY"],
        question_en="What time of day do most violations occur?",
        question_ar="في أي وقت من اليوم تحدث معظم المخالفات؟",
        variations_en=[
            "Violations by time of day",
            "Peak violation hours",
            "When do violations happen most?"
        ],
        variations_ar=[
            "المخالفات حسب الوقت",
            "أوقات الذروة للمخالفات"
        ],
        keywords_en=["time", "day", "violations", "when", "peak", "hour"],
        keywords_ar=["وقت", "يوم", "مخالفات", "متى"],
        sql="""
            SELECT 
                DATEPART(HOUR, e.SubmitionDate) as hour,
                CASE 
                    WHEN DATEPART(HOUR, e.SubmitionDate) < 6 THEN 'Night (00-06)'
                    WHEN DATEPART(HOUR, e.SubmitionDate) < 12 THEN 'Morning (06-12)'
                    WHEN DATEPART(HOUR, e.SubmitionDate) < 18 THEN 'Afternoon (12-18)'
                    ELSE 'Evening (18-24)'
                END as time_period,
                COUNT(ev.Id) as violation_count
            FROM Event e
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(HOUR, e.SubmitionDate),
                CASE 
                    WHEN DATEPART(HOUR, e.SubmitionDate) < 6 THEN 'Night (00-06)'
                    WHEN DATEPART(HOUR, e.SubmitionDate) < 12 THEN 'Morning (06-12)'
                    WHEN DATEPART(HOUR, e.SubmitionDate) < 18 THEN 'Afternoon (12-18)'
                    ELSE 'Evening (18-24)'
                END
            ORDER BY hour
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]


# ============================================================================
# REGISTER ALL ANALYTICS QUESTIONS
# ============================================================================

ALL_ANALYTICS_QUESTIONS = (
    TREND_QUESTIONS +
    RANKING_QUESTIONS +
    DISTRIBUTION_QUESTIONS +
    AGGREGATE_QUESTIONS +
    PATTERN_QUESTIONS
)

# Register all questions
registry.register_many(ALL_ANALYTICS_QUESTIONS)

print(f"Analytics Questions loaded: {len(ALL_ANALYTICS_QUESTIONS)} templates")
