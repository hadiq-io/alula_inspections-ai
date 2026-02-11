"""
Extended Analytics Questions Library
=====================================
50+ additional analytics questions covering advanced trends, correlations,
patterns, forecasting, and statistical analysis.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# CORRELATION ANALYSIS (10 questions)
# ============================================================================

CORRELATION_QUESTIONS = [
    QuestionTemplate(
        id="ANA_CORR_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "SCORE", "VIOLATIONS"],
        question_en="Is there a correlation between score and number of violations?",
        question_ar="هل هناك علاقة بين الدرجة وعدد المخالفات؟",
        variations_en=[
            "How do scores relate to violations?",
            "Score vs violations relationship",
            "Correlation between scores and violations"
        ],
        variations_ar=["علاقة الدرجات بالمخالفات", "الارتباط بين الدرجات والمخالفات"],
        keywords_en=["correlation", "relationship", "scores", "violations"],
        keywords_ar=["ارتباط", "علاقة", "درجات", "مخالفات"],
        sql="""
            SELECT e.Score, COUNT(ev.Id) as violation_count
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY e.Id, e.Score
            ORDER BY e.Score
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.SCATTER,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_CORR_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "LOCATION", "TIME"],
        question_en="Is there a pattern between inspection time and scores?",
        question_ar="هل هناك نمط بين وقت الفحص والدرجات؟",
        variations_en=[
            "Time of day vs scores",
            "Does time affect inspection scores?",
            "Score patterns by hour"
        ],
        variations_ar=["الوقت مقابل الدرجات", "هل يؤثر الوقت على الدرجات؟"],
        keywords_en=["time", "hour", "pattern", "scores"],
        keywords_ar=["وقت", "ساعة", "نمط", "درجات"],
        sql="""
            SELECT DATEPART(HOUR, e.SubmitionDate) as hour,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(*) as inspection_count
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(HOUR, e.SubmitionDate)
            ORDER BY hour
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_CORR_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "INSPECTOR", "LOCATION"],
        question_en="Do certain inspectors perform better at specific locations?",
        question_ar="هل بعض المفتشين يؤدون أفضل في مواقع معينة؟",
        variations_en=[
            "Inspector location performance",
            "Best inspector-location combinations",
            "Inspector performance by site"
        ],
        variations_ar=["أداء المفتش حسب الموقع", "أفضل مجموعات المفتش-الموقع"],
        keywords_en=["inspector", "location", "performance", "better"],
        keywords_ar=["مفتش", "موقع", "أداء", "أفضل"],
        sql="""
            SELECT u.Name as inspector, l.Name as location,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            JOIN [User] u ON e.ReporterID = u.Id
            JOIN Location l ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, l.Id, l.Name
            HAVING COUNT(e.Id) >= 3
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_CORR_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "WEATHER", "DAY"],
        question_en="How do scores vary by day of the week?",
        question_ar="كيف تختلف الدرجات حسب يوم الأسبوع؟",
        variations_en=[
            "Scores by weekday",
            "Day of week impact on scores",
            "Weekly pattern in scores"
        ],
        variations_ar=["الدرجات حسب اليوم", "تأثير اليوم على الدرجات"],
        keywords_en=["day", "week", "weekday", "pattern"],
        keywords_ar=["يوم", "أسبوع", "نمط"],
        sql="""
            SELECT DATENAME(WEEKDAY, e.SubmitionDate) as day_name,
                   DATEPART(WEEKDAY, e.SubmitionDate) as day_num,
                   COUNT(*) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(WEEKDAY, e.SubmitionDate), DATEPART(WEEKDAY, e.SubmitionDate)
            ORDER BY day_num
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_CORR_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "NEIGHBORHOOD", "VIOLATIONS"],
        question_en="Which neighborhoods have correlated violation patterns?",
        question_ar="أي الأحياء لديها أنماط مخالفات مترابطة؟",
        variations_en=[
            "Neighborhood violation patterns",
            "Similar violation areas",
            "Correlated neighborhood issues"
        ],
        variations_ar=["أنماط مخالفات الأحياء", "المناطق المتشابهة"],
        keywords_en=["neighborhood", "correlated", "patterns", "similar"],
        keywords_ar=["حي", "مترابط", "أنماط", "متشابه"],
        sql="""
            SELECT n.Name as neighborhood, vt.Name as violation_type, COUNT(*) as count
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
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_CORR_006",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "FREQUENCY", "QUALITY"],
        question_en="Does inspection frequency affect compliance?",
        question_ar="هل تكرار الفحص يؤثر على الامتثال؟",
        variations_en=[
            "Frequency vs compliance",
            "More inspections better compliance?",
            "Inspection frequency impact"
        ],
        variations_ar=["التكرار مقابل الامتثال", "هل كثرة الفحوصات تحسن الامتثال؟"],
        keywords_en=["frequency", "compliance", "affect", "more"],
        keywords_ar=["تكرار", "امتثال", "تأثير", "أكثر"],
        sql="""
            SELECT inspection_count_range, COUNT(*) as location_count,
                   CAST(AVG(avg_score) AS DECIMAL(5,2)) as avg_compliance_score
            FROM (
                SELECT l.Id,
                       CASE 
                           WHEN COUNT(e.Id) <= 2 THEN '1-2 inspections'
                           WHEN COUNT(e.Id) <= 5 THEN '3-5 inspections'
                           WHEN COUNT(e.Id) <= 10 THEN '6-10 inspections'
                           ELSE '10+ inspections'
                       END as inspection_count_range,
                       AVG(e.Score) as avg_score
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
            ) grouped
            GROUP BY inspection_count_range
            ORDER BY MIN(avg_score)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_CORR_007",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "SEASON", "VIOLATIONS"],
        question_en="Are violations seasonal?",
        question_ar="هل المخالفات موسمية؟",
        variations_en=[
            "Seasonal violation patterns",
            "Do violations change by season?",
            "Violation seasonality"
        ],
        variations_ar=["أنماط المخالفات الموسمية", "هل المخالفات تتغير بالموسم؟"],
        keywords_en=["seasonal", "season", "winter", "summer"],
        keywords_ar=["موسمي", "موسم", "شتاء", "صيف"],
        sql="""
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(ev.Id) as violation_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter' WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring' WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer' ELSE 'Fall' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_CORR_008",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "EXPERIENCE", "QUALITY"],
        question_en="Do more experienced inspectors have better scores?",
        question_ar="هل المفتشون الأكثر خبرة لديهم درجات أفضل؟",
        variations_en=[
            "Experience vs quality",
            "Inspector experience impact",
            "Does experience improve scores?"
        ],
        variations_ar=["الخبرة مقابل الجودة", "تأثير خبرة المفتش"],
        keywords_en=["experienced", "experience", "better", "quality"],
        keywords_ar=["خبرة", "خبير", "أفضل", "جودة"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as total_inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY total_inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.SCATTER,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_CORR_009",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "FIRST", "SUBSEQUENT"],
        question_en="How do first inspections compare to subsequent ones?",
        question_ar="كيف تقارن الفحوصات الأولى بالتالية؟",
        variations_en=[
            "First vs follow-up inspections",
            "Initial vs repeat inspection scores",
            "Improvement over inspections"
        ],
        variations_ar=["الفحص الأول مقابل المتابعة", "الأولي مقابل المتكرر"],
        keywords_en=["first", "subsequent", "follow-up", "repeat"],
        keywords_ar=["أول", "تالي", "متابعة", "متكرر"],
        sql="""
            WITH Numbered AS (
                SELECT e.*, ROW_NUMBER() OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as inspection_num
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT 
                CASE WHEN inspection_num = 1 THEN 'First Inspection' ELSE 'Subsequent Inspection' END as inspection_type,
                COUNT(*) as count,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Numbered
            GROUP BY CASE WHEN inspection_num = 1 THEN 'First Inspection' ELSE 'Subsequent Inspection' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_CORR_010",
        category=QuestionCategory.ANALYTICS,
        subcategory="correlation",
        intent=["CORRELATION", "CATEGORY", "SCORE"],
        question_en="Which violation categories most affect scores?",
        question_ar="أي فئات المخالفات تؤثر أكثر على الدرجات؟",
        variations_en=[
            "Violation category impact",
            "Categories affecting scores most",
            "Score impact by violation type"
        ],
        variations_ar=["تأثير فئة المخالفة", "الفئات الأكثر تأثيراً"],
        keywords_en=["category", "affect", "impact", "scores"],
        keywords_ar=["فئة", "تأثير", "أكثر", "درجات"],
        sql="""
            SELECT vc.Name as category,
                   COUNT(ev.Id) as violation_count,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_event_score
            FROM ViolationCategory vc
            JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY avg_event_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# STATISTICAL ANALYSIS (10 questions)
# ============================================================================

STATISTICAL_QUESTIONS = [
    QuestionTemplate(
        id="ANA_STAT_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["STATISTICS", "SUMMARY"],
        question_en="Give me statistical summary of inspection scores",
        question_ar="أعطني ملخصاً إحصائياً لدرجات الفحص",
        variations_en=[
            "Score statistics",
            "Statistical overview",
            "Descriptive statistics"
        ],
        variations_ar=["إحصائيات الدرجات", "نظرة إحصائية عامة"],
        keywords_en=["statistics", "summary", "average", "deviation"],
        keywords_ar=["إحصائيات", "ملخص", "متوسط", "انحراف"],
        sql="""
            SELECT 
                COUNT(*) as total_count,
                CAST(AVG(Score) AS DECIMAL(5,2)) as mean_score,
                CAST(STDEV(Score) AS DECIMAL(5,2)) as std_deviation,
                MIN(Score) as min_score,
                MAX(Score) as max_score,
                MAX(Score) - MIN(Score) as range_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_STAT_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["PERCENTILE", "SCORES"],
        question_en="What are the score percentiles?",
        question_ar="ما هي نسب مئوية الدرجات؟",
        variations_en=[
            "Score percentile distribution",
            "25th 50th 75th percentile",
            "Quartile distribution"
        ],
        variations_ar=["توزيع النسب المئوية", "الربعيات"],
        keywords_en=["percentile", "quartile", "distribution"],
        keywords_ar=["نسبة مئوية", "ربعي", "توزيع"],
        sql="""
            SELECT DISTINCT
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY Score) OVER () as p25,
                PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY Score) OVER () as p50_median,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY Score) OVER () as p75,
                PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY Score) OVER () as p90
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_STAT_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["OUTLIERS", "SCORES"],
        question_en="Are there any score outliers?",
        question_ar="هل هناك قيم متطرفة في الدرجات؟",
        variations_en=[
            "Outlier detection",
            "Anomalous scores",
            "Unusual score values"
        ],
        variations_ar=["اكتشاف القيم المتطرفة", "درجات غير عادية"],
        keywords_en=["outliers", "anomalous", "unusual", "extreme"],
        keywords_ar=["متطرف", "غير عادي", "شاذ"],
        sql="""
            WITH Stats AS (
                SELECT AVG(Score) as mean_score, STDEV(Score) as std_dev
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            )
            SELECT e.Id, e.Score, l.Name as location,
                   CAST((e.Score - s.mean_score) / NULLIF(s.std_dev, 0) AS DECIMAL(5,2)) as z_score
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            CROSS JOIN Stats s
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            AND ABS(e.Score - s.mean_score) > 2 * s.std_dev
            ORDER BY ABS(e.Score - s.mean_score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_STAT_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["MODE", "COMMON"],
        question_en="What is the most common score range?",
        question_ar="ما هو نطاق الدرجات الأكثر شيوعاً؟",
        variations_en=[
            "Most frequent scores",
            "Common score values",
            "Score mode"
        ],
        variations_ar=["الدرجات الأكثر تكراراً", "القيم الشائعة"],
        keywords_en=["common", "frequent", "mode", "typical"],
        keywords_ar=["شائع", "متكرر", "نموذجي"],
        sql="""
            SELECT 
                FLOOR(Score / 10) * 10 as score_range_start,
                FLOOR(Score / 10) * 10 + 9 as score_range_end,
                COUNT(*) as frequency
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY FLOOR(Score / 10)
            ORDER BY frequency DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_STAT_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["VARIANCE", "LOCATIONS"],
        question_en="Which locations have the highest score variance?",
        question_ar="أي المواقع لديها أعلى تباين في الدرجات؟",
        variations_en=[
            "Score variance by location",
            "Inconsistent scoring locations",
            "High variance sites"
        ],
        variations_ar=["تباين الدرجات حسب الموقع", "المواقع غير المتسقة"],
        keywords_en=["variance", "inconsistent", "variable"],
        keywords_ar=["تباين", "غير متسق", "متغير"],
        sql="""
            SELECT TOP 10 l.Name as location,
                   COUNT(e.Id) as inspection_count,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(STDEV(e.Score) AS DECIMAL(5,2)) as score_std_dev,
                   MAX(e.Score) - MIN(e.Score) as score_range
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(e.Id) >= 3
            ORDER BY STDEV(e.Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_STAT_006",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["TREND", "STATISTICAL"],
        question_en="What is the statistical trend of scores?",
        question_ar="ما هو الاتجاه الإحصائي للدرجات؟",
        variations_en=[
            "Score trend analysis",
            "Is there a trend in scores?",
            "Statistical trend"
        ],
        variations_ar=["تحليل اتجاه الدرجات", "هل هناك اتجاه؟"],
        keywords_en=["trend", "increasing", "decreasing", "statistical"],
        keywords_ar=["اتجاه", "يزداد", "ينخفض", "إحصائي"],
        sql="""
            SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                   CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(*) as count
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_STAT_007",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["CONFIDENCE", "INTERVAL"],
        question_en="What is the confidence interval for average score?",
        question_ar="ما هو فاصل الثقة لمتوسط الدرجة؟",
        variations_en=[
            "Score confidence interval",
            "Average score range",
            "Statistical confidence"
        ],
        variations_ar=["فاصل الثقة للدرجة", "نطاق المتوسط"],
        keywords_en=["confidence", "interval", "range", "95%"],
        keywords_ar=["ثقة", "فاصل", "نطاق"],
        sql="""
            SELECT 
                CAST(AVG(Score) AS DECIMAL(5,2)) as mean_score,
                CAST(STDEV(Score) AS DECIMAL(5,2)) as std_dev,
                COUNT(*) as n,
                CAST(AVG(Score) - 1.96 * STDEV(Score) / SQRT(COUNT(*)) AS DECIMAL(5,2)) as ci_lower_95,
                CAST(AVG(Score) + 1.96 * STDEV(Score) / SQRT(COUNT(*)) AS DECIMAL(5,2)) as ci_upper_95
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_STAT_008",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["SKEWNESS", "DISTRIBUTION"],
        question_en="Is the score distribution normal or skewed?",
        question_ar="هل توزيع الدرجات طبيعي أم منحرف؟",
        variations_en=[
            "Score distribution shape",
            "Normal distribution check",
            "Distribution skewness"
        ],
        variations_ar=["شكل توزيع الدرجات", "فحص التوزيع الطبيعي"],
        keywords_en=["normal", "skewed", "distribution", "shape"],
        keywords_ar=["طبيعي", "منحرف", "توزيع", "شكل"],
        sql="""
            SELECT 
                CAST(AVG(Score) AS DECIMAL(5,2)) as mean,
                (SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Score) OVER () FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as median,
                CASE 
                    WHEN AVG(Score) > (SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Score) OVER () FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year})
                    THEN 'Right-skewed (positive)'
                    WHEN AVG(Score) < (SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Score) OVER () FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year})
                    THEN 'Left-skewed (negative)'
                    ELSE 'Approximately normal'
                END as distribution_shape
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_STAT_009",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["COEFFICIENT", "VARIATION"],
        question_en="What is the coefficient of variation?",
        question_ar="ما هو معامل التباين؟",
        variations_en=[
            "CV of scores",
            "Relative variability",
            "Score CV"
        ],
        variations_ar=["معامل التباين للدرجات", "التباين النسبي"],
        keywords_en=["coefficient", "variation", "cv", "relative"],
        keywords_ar=["معامل", "تباين", "نسبي"],
        sql="""
            SELECT 
                CAST(AVG(Score) AS DECIMAL(5,2)) as mean,
                CAST(STDEV(Score) AS DECIMAL(5,2)) as std_dev,
                CAST(STDEV(Score) * 100.0 / NULLIF(AVG(Score), 0) AS DECIMAL(5,2)) as coefficient_of_variation
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_STAT_010",
        category=QuestionCategory.ANALYTICS,
        subcategory="statistics",
        intent=["HISTOGRAM", "SCORES"],
        question_en="Show me a histogram of scores",
        question_ar="أظهر لي رسماً بيانياً للدرجات",
        variations_en=[
            "Score histogram",
            "Score frequency chart",
            "Distribution histogram"
        ],
        variations_ar=["رسم بياني للدرجات", "مخطط التكرار"],
        keywords_en=["histogram", "frequency", "chart", "bins"],
        keywords_ar=["رسم بياني", "تكرار", "مخطط"],
        sql="""
            SELECT 
                CASE 
                    WHEN Score < 50 THEN '0-49'
                    WHEN Score < 60 THEN '50-59'
                    WHEN Score < 70 THEN '60-69'
                    WHEN Score < 80 THEN '70-79'
                    WHEN Score < 90 THEN '80-89'
                    ELSE '90-100'
                END as score_bin,
                COUNT(*) as frequency
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY CASE WHEN Score < 50 THEN '0-49' WHEN Score < 60 THEN '50-59' WHEN Score < 70 THEN '60-69' WHEN Score < 80 THEN '70-79' WHEN Score < 90 THEN '80-89' ELSE '90-100' END
            ORDER BY MIN(Score)
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# GEOGRAPHIC ANALYSIS (10 questions)
# ============================================================================

GEOGRAPHIC_QUESTIONS = [
    QuestionTemplate(
        id="ANA_GEO_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["GEOGRAPHIC", "DISTRIBUTION"],
        question_en="How are inspections distributed across neighborhoods?",
        question_ar="كيف توزع الفحوصات على الأحياء؟",
        variations_en=[
            "Neighborhood inspection distribution",
            "Inspections by area",
            "Geographic spread of inspections"
        ],
        variations_ar=["توزيع الفحوصات على الأحياء", "الفحوصات حسب المنطقة"],
        keywords_en=["geographic", "distribution", "neighborhood", "area"],
        keywords_ar=["جغرافي", "توزيع", "حي", "منطقة"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspection_count,
                   COUNT(DISTINCT l.Id) as location_count,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_GEO_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["HOTSPOT", "VIOLATIONS"],
        question_en="Where are the violation hotspots?",
        question_ar="أين تتركز المخالفات؟",
        variations_en=[
            "Violation concentration areas",
            "High violation areas",
            "Problem areas"
        ],
        variations_ar=["مناطق تركز المخالفات", "المناطق ذات المخالفات العالية"],
        keywords_en=["hotspot", "concentration", "area", "high"],
        keywords_ar=["تركز", "منطقة", "عالي"],
        sql="""
            SELECT TOP 10 n.Name as neighborhood,
                   COUNT(ev.Id) as violation_count,
                   COUNT(DISTINCT l.Id) as affected_locations
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY violation_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_GEO_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["COVERAGE", "GAP"],
        question_en="Which areas have inspection coverage gaps?",
        question_ar="أي المناطق لديها فجوات في تغطية الفحص؟",
        variations_en=[
            "Underinspected areas",
            "Coverage gaps",
            "Areas needing more inspections"
        ],
        variations_ar=["المناطق قليلة الفحص", "فجوات التغطية"],
        keywords_en=["coverage", "gap", "underinspected", "missing"],
        keywords_ar=["تغطية", "فجوة", "قليل الفحص"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(DISTINCT l.Id) as total_locations,
                   COUNT(DISTINCT e.LocationID) as inspected_locations,
                   COUNT(DISTINCT l.Id) - COUNT(DISTINCT e.LocationID) as uninspected_locations
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id AND l.IsDeleted = 0
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            HAVING COUNT(DISTINCT l.Id) - COUNT(DISTINCT e.LocationID) > 0
            ORDER BY uninspected_locations DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_GEO_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["BEST", "NEIGHBORHOODS"],
        question_en="Which neighborhoods have the best compliance?",
        question_ar="أي الأحياء لديها أفضل امتثال؟",
        variations_en=[
            "Top performing neighborhoods",
            "Best compliance areas",
            "Highest scoring neighborhoods"
        ],
        variations_ar=["الأحياء الأفضل أداءً", "مناطق الامتثال الأعلى"],
        keywords_en=["best", "top", "highest", "compliance"],
        keywords_ar=["أفضل", "أعلى", "امتثال"],
        sql="""
            SELECT TOP 10 n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            HAVING COUNT(e.Id) >= 5
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_GEO_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["WORST", "NEIGHBORHOODS"],
        question_en="Which neighborhoods need the most attention?",
        question_ar="أي الأحياء تحتاج أكثر اهتمام؟",
        variations_en=[
            "Lowest performing neighborhoods",
            "Problem neighborhoods",
            "Areas needing improvement"
        ],
        variations_ar=["الأحياء الأدنى أداءً", "المناطق المشكلة"],
        keywords_en=["worst", "lowest", "attention", "problem"],
        keywords_ar=["أسوأ", "أدنى", "اهتمام", "مشكلة"],
        sql="""
            SELECT TOP 10 n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            HAVING COUNT(e.Id) >= 3
            ORDER BY AVG(e.Score) ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_GEO_006",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["CLUSTER", "VIOLATIONS"],
        question_en="Are there violation clusters in specific areas?",
        question_ar="هل هناك تجمعات للمخالفات في مناطق معينة؟",
        variations_en=[
            "Violation clustering",
            "Grouped violations",
            "Concentrated problem areas"
        ],
        variations_ar=["تجمع المخالفات", "المخالفات المتجمعة"],
        keywords_en=["cluster", "grouped", "concentrated", "specific"],
        keywords_ar=["تجمع", "متجمع", "مركز", "معين"],
        sql="""
            SELECT n.Name as neighborhood, vt.Name as violation_type,
                   COUNT(*) as occurrence_count
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, vt.Id, vt.Name
            HAVING COUNT(*) >= 3
            ORDER BY occurrence_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_GEO_007",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["DENSITY", "LOCATIONS"],
        question_en="What is the location density by neighborhood?",
        question_ar="ما هي كثافة المواقع حسب الحي؟",
        variations_en=[
            "Locations per neighborhood",
            "Location distribution",
            "Site density"
        ],
        variations_ar=["المواقع لكل حي", "توزيع المواقع"],
        keywords_en=["density", "locations", "per neighborhood"],
        keywords_ar=["كثافة", "مواقع", "لكل حي"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(l.Id) as location_count
            FROM Neighborhood n
            LEFT JOIN Location l ON l.NeighborhoodID = n.Id AND l.IsDeleted = 0
            GROUP BY n.Id, n.Name
            ORDER BY location_count DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_GEO_008",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["IMPROVEMENT", "AREAS"],
        question_en="Which areas have improved the most?",
        question_ar="أي المناطق تحسنت أكثر؟",
        variations_en=[
            "Most improved areas",
            "Neighborhood improvements",
            "Best improving regions"
        ],
        variations_ar=["المناطق الأكثر تحسناً", "تحسينات الأحياء"],
        keywords_en=["improved", "improvement", "better", "areas"],
        keywords_ar=["تحسن", "تحسين", "أفضل", "مناطق"],
        sql="""
            SELECT n.Name as neighborhood,
                   curr.avg_score as current_avg,
                   prev.avg_score as previous_avg,
                   curr.avg_score - prev.avg_score as improvement
            FROM Neighborhood n
            JOIN (
                SELECT l.NeighborhoodID, AVG(e.Score) as avg_score
                FROM Location l JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.NeighborhoodID
            ) curr ON curr.NeighborhoodID = n.Id
            JOIN (
                SELECT l.NeighborhoodID, AVG(e.Score) as avg_score
                FROM Location l JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year} - 1
                GROUP BY l.NeighborhoodID
            ) prev ON prev.NeighborhoodID = n.Id
            ORDER BY improvement DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_GEO_009",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["INSPECTOR", "COVERAGE", "AREA"],
        question_en="How is inspector coverage distributed by area?",
        question_ar="كيف توزع تغطية المفتشين حسب المنطقة؟",
        variations_en=[
            "Inspector distribution by neighborhood",
            "Area inspector assignment",
            "Inspector coverage map"
        ],
        variations_ar=["توزيع المفتشين حسب الحي", "تعيين المفتشين بالمنطقة"],
        keywords_en=["inspector", "coverage", "area", "distribution"],
        keywords_ar=["مفتش", "تغطية", "منطقة", "توزيع"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(DISTINCT e.ReporterID) as inspectors,
                   COUNT(e.Id) as inspections
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY inspectors DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_GEO_010",
        category=QuestionCategory.ANALYTICS,
        subcategory="geographic",
        intent=["HERITAGE", "ZONE"],
        question_en="What is the compliance rate in heritage zones?",
        question_ar="ما معدل الامتثال في مناطق التراث؟",
        variations_en=[
            "Heritage zone compliance",
            "Historical area compliance",
            "Cultural site compliance"
        ],
        variations_ar=["امتثال مناطق التراث", "امتثال المناطق التاريخية"],
        keywords_en=["heritage", "zone", "historical", "cultural"],
        keywords_ar=["تراث", "منطقة", "تاريخي", "ثقافي"],
        sql="""
            SELECT n.Name as zone,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
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
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# PATTERN DETECTION (10 questions)
# ============================================================================

PATTERN_QUESTIONS = [
    QuestionTemplate(
        id="ANA_PAT_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "RECURRING"],
        question_en="What are the most recurring violation patterns?",
        question_ar="ما هي أنماط المخالفات الأكثر تكراراً؟",
        variations_en=[
            "Recurring violations",
            "Common violation patterns",
            "Repeated issues"
        ],
        variations_ar=["المخالفات المتكررة", "أنماط المخالفات الشائعة"],
        keywords_en=["pattern", "recurring", "repeated", "common"],
        keywords_ar=["نمط", "متكرر", "شائع"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(*) as occurrences,
                   COUNT(DISTINCT e.LocationID) as locations_affected
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            ORDER BY occurrences DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_PAT_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "WEEKLY"],
        question_en="Is there a weekly pattern in inspections?",
        question_ar="هل هناك نمط أسبوعي في الفحوصات؟",
        variations_en=[
            "Weekly inspection pattern",
            "Day of week trends",
            "Weekly cycle"
        ],
        variations_ar=["نمط الفحص الأسبوعي", "اتجاهات أيام الأسبوع"],
        keywords_en=["weekly", "pattern", "day", "cycle"],
        keywords_ar=["أسبوعي", "نمط", "يوم", "دورة"],
        sql="""
            SELECT DATENAME(WEEKDAY, SubmitionDate) as day_name,
                   DATEPART(WEEKDAY, SubmitionDate) as day_num,
                   COUNT(*) as inspections,
                   CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY DATENAME(WEEKDAY, SubmitionDate), DATEPART(WEEKDAY, SubmitionDate)
            ORDER BY day_num
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_PAT_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "MONTHLY"],
        question_en="Is there a monthly pattern in violations?",
        question_ar="هل هناك نمط شهري في المخالفات؟",
        variations_en=[
            "Monthly violation pattern",
            "Violations by month",
            "Monthly trends"
        ],
        variations_ar=["نمط المخالفات الشهري", "المخالفات حسب الشهر"],
        keywords_en=["monthly", "pattern", "month", "trend"],
        keywords_ar=["شهري", "نمط", "شهر", "اتجاه"],
        sql="""
            SELECT DATENAME(MONTH, e.SubmitionDate) as month_name,
                   MONTH(e.SubmitionDate) as month_num,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATENAME(MONTH, e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY month_num
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_PAT_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "CONSECUTIVE"],
        question_en="Are there locations with consecutive low scores?",
        question_ar="هل هناك مواقع بدرجات منخفضة متتالية؟",
        variations_en=[
            "Consecutive low scores",
            "Repeated failures",
            "Persistent problems"
        ],
        variations_ar=["درجات منخفضة متتالية", "فشل متكرر"],
        keywords_en=["consecutive", "low", "repeated", "persistent"],
        keywords_ar=["متتالي", "منخفض", "متكرر", "مستمر"],
        sql="""
            WITH Ranked AS (
                SELECT e.LocationID, e.Score, e.SubmitionDate,
                       LAG(e.Score) OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as prev_score
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT l.Name as location, COUNT(*) as consecutive_low_count
            FROM Ranked r
            JOIN Location l ON r.LocationID = l.Id
            WHERE r.Score < 80 AND r.prev_score < 80
            GROUP BY r.LocationID, l.Name
            ORDER BY consecutive_low_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_PAT_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "IMPROVEMENT"],
        question_en="Which locations show consistent improvement?",
        question_ar="أي المواقع تظهر تحسناً مستمراً؟",
        variations_en=[
            "Improving locations",
            "Consistent improvement",
            "Upward trend locations"
        ],
        variations_ar=["المواقع المتحسنة", "تحسن مستمر"],
        keywords_en=["improvement", "consistent", "upward", "better"],
        keywords_ar=["تحسن", "مستمر", "صعود", "أفضل"],
        sql="""
            WITH Ranked AS (
                SELECT e.LocationID, e.Score, e.SubmitionDate,
                       LAG(e.Score) OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as prev_score
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT l.Name as location, COUNT(*) as improvement_count
            FROM Ranked r
            JOIN Location l ON r.LocationID = l.Id
            WHERE r.Score > r.prev_score AND r.prev_score IS NOT NULL
            GROUP BY r.LocationID, l.Name
            HAVING COUNT(*) >= 2
            ORDER BY improvement_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_PAT_006",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "VIOLATION", "COMBINATION"],
        question_en="Which violations commonly occur together?",
        question_ar="أي المخالفات تحدث معاً عادةً؟",
        variations_en=[
            "Co-occurring violations",
            "Violation combinations",
            "Related violations"
        ],
        variations_ar=["المخالفات المتزامنة", "مجموعات المخالفات"],
        keywords_en=["together", "combination", "co-occur", "related"],
        keywords_ar=["معاً", "مجموعة", "متزامن", "مرتبط"],
        sql="""
            SELECT vt1.Name as violation1, vt2.Name as violation2,
                   COUNT(*) as co_occurrence_count
            FROM EventViolation ev1
            JOIN EventViolation ev2 ON ev1.EventId = ev2.EventId AND ev1.ViolationTypeId < ev2.ViolationTypeId
            JOIN ViolationType vt1 ON ev1.ViolationTypeId = vt1.Id
            JOIN ViolationType vt2 ON ev2.ViolationTypeId = vt2.Id
            JOIN Event e ON ev1.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt1.Id, vt1.Name, vt2.Id, vt2.Name
            HAVING COUNT(*) >= 2
            ORDER BY co_occurrence_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_PAT_007",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "INSPECTOR", "BEHAVIOR"],
        question_en="Are there patterns in inspector behavior?",
        question_ar="هل هناك أنماط في سلوك المفتش؟",
        variations_en=[
            "Inspector patterns",
            "Inspector behavior trends",
            "Inspector consistency"
        ],
        variations_ar=["أنماط المفتش", "اتجاهات سلوك المفتش"],
        keywords_en=["inspector", "pattern", "behavior", "consistency"],
        keywords_ar=["مفتش", "نمط", "سلوك", "اتساق"],
        sql="""
            SELECT u.Name as inspector,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(STDEV(e.Score) AS DECIMAL(5,2)) as score_variation,
                   COUNT(*) as inspection_count
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(*) >= 5
            ORDER BY score_variation DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_PAT_008",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "TIME", "SERIES"],
        question_en="What does the time series of scores look like?",
        question_ar="كيف يبدو التسلسل الزمني للدرجات؟",
        variations_en=[
            "Score time series",
            "Historical score trend",
            "Score over time"
        ],
        variations_ar=["التسلسل الزمني للدرجات", "اتجاه الدرجات التاريخي"],
        keywords_en=["time series", "historical", "trend", "over time"],
        keywords_ar=["تسلسل زمني", "تاريخي", "اتجاه", "مع الوقت"],
        sql="""
            SELECT CAST(SubmitionDate AS DATE) as date,
                   COUNT(*) as inspections,
                   CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY CAST(SubmitionDate AS DATE)
            ORDER BY date
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_PAT_009",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["ANOMALY", "DETECTION"],
        question_en="Are there any anomalous inspection patterns?",
        question_ar="هل هناك أي أنماط فحص شاذة؟",
        variations_en=[
            "Unusual patterns",
            "Anomalies in data",
            "Strange inspection patterns"
        ],
        variations_ar=["أنماط غير عادية", "شذوذ في البيانات"],
        keywords_en=["anomaly", "unusual", "strange", "abnormal"],
        keywords_ar=["شاذ", "غير عادي", "غريب"],
        sql="""
            SELECT CAST(e.SubmitionDate AS DATE) as date,
                   COUNT(*) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CAST(e.SubmitionDate AS DATE)
            HAVING COUNT(*) > (
                SELECT AVG(daily_count) + 2 * STDEV(daily_count)
                FROM (
                    SELECT COUNT(*) as daily_count
                    FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
                    GROUP BY CAST(SubmitionDate AS DATE)
                ) daily
            )
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_PAT_010",
        category=QuestionCategory.ANALYTICS,
        subcategory="patterns",
        intent=["PATTERN", "QUARTERLY"],
        question_en="What is the quarterly pattern of performance?",
        question_ar="ما هو النمط الربع سنوي للأداء؟",
        variations_en=[
            "Quarterly performance",
            "Q1 Q2 Q3 Q4 comparison",
            "Quarter over quarter"
        ],
        variations_ar=["الأداء الربع سنوي", "مقارنة الأرباع"],
        keywords_en=["quarterly", "quarter", "q1", "q2", "q3", "q4"],
        keywords_ar=["ربع سنوي", "ربع"],
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
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# COMPARATIVE ANALYSIS (10 questions)
# ============================================================================

COMPARATIVE_QUESTIONS = [
    QuestionTemplate(
        id="ANA_COMP_001",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["COMPARE", "PERIODS"],
        question_en="Compare this quarter to last quarter",
        question_ar="قارن هذا الربع بالربع السابق",
        variations_en=[
            "Quarter comparison",
            "This vs last quarter",
            "QoQ comparison"
        ],
        variations_ar=["مقارنة الأرباع", "هذا مقابل الربع الماضي"],
        keywords_en=["compare", "quarter", "last", "this"],
        keywords_ar=["قارن", "ربع", "الماضي", "هذا"],
        sql="""
            SELECT 
                'Current Quarter' as period,
                COUNT(*) as inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event WHERE IsDeleted = 0 
            AND DATEPART(QUARTER, SubmitionDate) = DATEPART(QUARTER, GETDATE())
            AND YEAR(SubmitionDate) = YEAR(GETDATE())
            UNION ALL
            SELECT 
                'Previous Quarter',
                COUNT(*),
                CAST(AVG(Score) AS DECIMAL(5,2))
            FROM Event WHERE IsDeleted = 0 
            AND DATEPART(QUARTER, SubmitionDate) = DATEPART(QUARTER, DATEADD(QUARTER, -1, GETDATE()))
            AND YEAR(SubmitionDate) = YEAR(DATEADD(QUARTER, -1, GETDATE()))
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_COMP_002",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["BENCHMARK", "LOCATION"],
        question_en="How does each location compare to average?",
        question_ar="كيف يقارن كل موقع بالمتوسط؟",
        variations_en=[
            "Location vs average",
            "Above/below average locations",
            "Location benchmarking"
        ],
        variations_ar=["الموقع مقابل المتوسط", "المواقع فوق/تحت المتوسط"],
        keywords_en=["compare", "average", "benchmark", "location"],
        keywords_ar=["قارن", "متوسط", "معيار", "موقع"],
        sql="""
            WITH OverallAvg AS (
                SELECT AVG(Score) as overall_avg FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            )
            SELECT l.Name as location,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as location_avg,
                   CAST(o.overall_avg AS DECIMAL(5,2)) as overall_avg,
                   CAST(AVG(e.Score) - o.overall_avg AS DECIMAL(5,2)) as difference
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            CROSS JOIN OverallAvg o
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name, o.overall_avg
            ORDER BY difference DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_COMP_003",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["RANK", "INSPECTORS"],
        question_en="Rank inspectors by performance",
        question_ar="رتب المفتشين حسب الأداء",
        variations_en=[
            "Inspector ranking",
            "Best to worst inspectors",
            "Inspector performance ranking"
        ],
        variations_ar=["ترتيب المفتشين", "من الأفضل للأسوأ"],
        keywords_en=["rank", "performance", "inspector", "order"],
        keywords_ar=["ترتيب", "أداء", "مفتش"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   RANK() OVER (ORDER BY AVG(e.Score) DESC) as rank
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY rank
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_COMP_004",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["COMPARE", "VIOLATION", "TYPES"],
        question_en="Compare violation types by frequency and severity",
        question_ar="قارن أنواع المخالفات حسب التكرار والشدة",
        variations_en=[
            "Violation type comparison",
            "Frequency vs severity",
            "Violation analysis"
        ],
        variations_ar=["مقارنة أنواع المخالفات", "التكرار مقابل الشدة"],
        keywords_en=["violation", "type", "frequency", "severity"],
        keywords_ar=["مخالفة", "نوع", "تكرار", "شدة"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(ev.Id) as frequency,
                   AVG(ev.Value) as avg_value,
                   SUM(ev.Value) as total_value
            FROM ViolationType vt
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            ORDER BY frequency DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_COMP_005",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["MONTH", "OVER", "MONTH"],
        question_en="Compare month over month performance",
        question_ar="قارن الأداء شهراً بشهر",
        variations_en=[
            "Month to month comparison",
            "Monthly changes",
            "MoM performance"
        ],
        variations_ar=["مقارنة شهر بشهر", "التغيرات الشهرية"],
        keywords_en=["month", "over", "comparison", "change"],
        keywords_ar=["شهر", "مقارنة", "تغيير"],
        sql="""
            WITH MonthlyData AS (
                SELECT FORMAT(SubmitionDate, 'yyyy-MM') as month,
                       COUNT(*) as inspections,
                       AVG(Score) as avg_score
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
                GROUP BY FORMAT(SubmitionDate, 'yyyy-MM')
            )
            SELECT m1.month,
                   m1.inspections,
                   CAST(m1.avg_score AS DECIMAL(5,2)) as avg_score,
                   CAST(m1.avg_score - m2.avg_score AS DECIMAL(5,2)) as change_from_prev
            FROM MonthlyData m1
            LEFT JOIN MonthlyData m2 ON m2.month = FORMAT(DATEADD(MONTH, -1, CAST(m1.month + '-01' AS DATE)), 'yyyy-MM')
            ORDER BY m1.month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ANA_COMP_006",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["CATEGORY", "COMPARISON"],
        question_en="Compare compliance across violation categories",
        question_ar="قارن الامتثال عبر فئات المخالفات",
        variations_en=[
            "Category compliance comparison",
            "Compare by category",
            "Category-wise analysis"
        ],
        variations_ar=["مقارنة الامتثال بالفئة", "قارن حسب الفئة"],
        keywords_en=["category", "comparison", "across", "compliance"],
        keywords_ar=["فئة", "مقارنة", "عبر", "امتثال"],
        sql="""
            SELECT vc.Name as category,
                   COUNT(DISTINCT e.Id) as inspections,
                   COUNT(ev.Id) as violations,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM ViolationCategory vc
            LEFT JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            LEFT JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            LEFT JOIN Event e ON ev.EventId = e.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_COMP_007",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["WEEKDAY", "WEEKEND"],
        question_en="Compare weekday vs weekend performance",
        question_ar="قارن أداء أيام الأسبوع بعطلة الأسبوع",
        variations_en=[
            "Weekday weekend comparison",
            "Workday vs weekend",
            "Business days vs weekends"
        ],
        variations_ar=["مقارنة أيام العمل بالعطلة", "أيام الأسبوع مقابل العطلة"],
        keywords_en=["weekday", "weekend", "compare", "workday"],
        keywords_ar=["يوم عمل", "عطلة", "قارن"],
        sql="""
            SELECT 
                CASE WHEN DATEPART(WEEKDAY, SubmitionDate) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END as day_type,
                COUNT(*) as inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY CASE WHEN DATEPART(WEEKDAY, SubmitionDate) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_COMP_008",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["TOP", "BOTTOM"],
        question_en="Compare top 5 vs bottom 5 locations",
        question_ar="قارن أفضل 5 مواقع بأسوأ 5",
        variations_en=[
            "Best vs worst locations",
            "Top bottom comparison",
            "Extremes comparison"
        ],
        variations_ar=["الأفضل مقابل الأسوأ", "مقارنة الأعلى والأدنى"],
        keywords_en=["top", "bottom", "best", "worst", "compare"],
        keywords_ar=["أفضل", "أسوأ", "أعلى", "أدنى", "قارن"],
        sql="""
            WITH LocationScores AS (
                SELECT l.Name, AVG(e.Score) as avg_score,
                       RANK() OVER (ORDER BY AVG(e.Score) DESC) as rank_top,
                       RANK() OVER (ORDER BY AVG(e.Score) ASC) as rank_bottom
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id, l.Name
            )
            SELECT Name as location, CAST(avg_score AS DECIMAL(5,2)) as avg_score,
                   CASE WHEN rank_top <= 5 THEN 'Top 5' ELSE 'Bottom 5' END as category
            FROM LocationScores
            WHERE rank_top <= 5 OR rank_bottom <= 5
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ANA_COMP_009",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["FIRST", "HALF", "SECOND"],
        question_en="Compare first half vs second half of year",
        question_ar="قارن النصف الأول بالنصف الثاني من العام",
        variations_en=[
            "H1 vs H2 comparison",
            "First vs second half",
            "Half year comparison"
        ],
        variations_ar=["مقارنة النصف الأول بالثاني", "نصف السنة"],
        keywords_en=["first", "second", "half", "h1", "h2"],
        keywords_ar=["أول", "ثاني", "نصف"],
        sql="""
            SELECT 
                CASE WHEN MONTH(SubmitionDate) <= 6 THEN 'H1' ELSE 'H2' END as half,
                COUNT(*) as inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY CASE WHEN MONTH(SubmitionDate) <= 6 THEN 'H1' ELSE 'H2' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ANA_COMP_010",
        category=QuestionCategory.ANALYTICS,
        subcategory="comparative",
        intent=["TARGET", "ACTUAL"],
        question_en="Compare actual performance vs targets",
        question_ar="قارن الأداء الفعلي بالأهداف",
        variations_en=[
            "Actual vs target",
            "Target achievement",
            "Performance vs goals"
        ],
        variations_ar=["الفعلي مقابل المستهدف", "تحقيق الأهداف"],
        keywords_en=["actual", "target", "vs", "goal"],
        keywords_ar=["فعلي", "مستهدف", "هدف"],
        sql="""
            SELECT 
                'Compliance Rate' as metric,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as actual,
                85.0 as target,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) - 85.0 AS DECIMAL(5,2)) as variance
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
]


# ============================================================================
# REGISTER ALL EXTENDED ANALYTICS QUESTIONS
# ============================================================================

ALL_EXTENDED_ANALYTICS_QUESTIONS = (
    CORRELATION_QUESTIONS +
    STATISTICAL_QUESTIONS +
    GEOGRAPHIC_QUESTIONS +
    PATTERN_QUESTIONS +
    COMPARATIVE_QUESTIONS
)

# Register all questions
registry.register_many(ALL_EXTENDED_ANALYTICS_QUESTIONS)

print(f"Extended Analytics Questions loaded: {len(ALL_EXTENDED_ANALYTICS_QUESTIONS)} templates")
