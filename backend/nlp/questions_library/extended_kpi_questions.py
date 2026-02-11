"""
Extended KPI Questions Library
==============================
50+ additional KPI-related questions covering advanced compliance, performance metrics,
operational KPIs, safety metrics, and management dashboards.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# ADVANCED COMPLIANCE KPIs (10 questions)
# ============================================================================

ADVANCED_COMPLIANCE_QUESTIONS = [
    QuestionTemplate(
        id="KPI_ADV_COMP_001",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "THRESHOLD"],
        question_en="What percentage of locations are below the compliance threshold?",
        question_ar="ما نسبة المواقع التي تقل عن حد الامتثال؟",
        variations_en=[
            "How many locations are non-compliant?",
            "Locations below compliance threshold",
            "Non-compliant location percentage"
        ],
        variations_ar=["المواقع غير الممتثلة", "نسبة المواقع دون الحد"],
        keywords_en=["below", "threshold", "non-compliant", "locations"],
        keywords_ar=["دون", "حد", "غير ممتثل", "مواقع"],
        sql="""
            SELECT 
                COUNT(CASE WHEN avg_score < 80 THEN 1 END) as non_compliant_count,
                COUNT(*) as total_locations,
                CAST(COUNT(CASE WHEN avg_score < 80 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as non_compliant_pct
            FROM (
                SELECT l.Id, AVG(e.Score) as avg_score
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
            ) loc_scores
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_002",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "IMPROVEMENT"],
        question_en="Which locations improved their compliance the most?",
        question_ar="أي المواقع حسنت امتثالها أكثر؟",
        variations_en=[
            "Top compliance improvers",
            "Best improving locations",
            "Locations with biggest compliance gains"
        ],
        variations_ar=["أكثر المواقع تحسناً", "أفضل التحسينات"],
        keywords_en=["improved", "compliance", "most", "gains"],
        keywords_ar=["تحسن", "امتثال", "أكثر"],
        sql="""
            SELECT TOP 10
                l.Name as location_name,
                curr.avg_score as current_score,
                prev.avg_score as previous_score,
                curr.avg_score - prev.avg_score as improvement
            FROM Location l
            JOIN (
                SELECT LocationID, AVG(Score) as avg_score
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
                GROUP BY LocationID
            ) curr ON curr.LocationID = l.Id
            JOIN (
                SELECT LocationID, AVG(Score) as avg_score
                FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year} - 1
                GROUP BY LocationID
            ) prev ON prev.LocationID = l.Id
            ORDER BY improvement DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_003",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "STREAK"],
        question_en="Which locations have maintained 100% compliance?",
        question_ar="أي المواقع حافظت على امتثال 100%؟",
        variations_en=[
            "Perfect compliance locations",
            "Locations with no violations",
            "100% compliant sites"
        ],
        variations_ar=["مواقع الامتثال الكامل", "مواقع بدون مخالفات"],
        keywords_en=["100%", "perfect", "maintained", "compliance"],
        keywords_ar=["100%", "كامل", "حافظ", "امتثال"],
        sql="""
            SELECT l.Name as location_name, COUNT(e.Id) as inspection_count, 
                   AVG(e.Score) as avg_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING MIN(e.Score) >= 80
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_004",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "CRITICAL"],
        question_en="How many critical compliance failures occurred?",
        question_ar="كم عدد حالات فشل الامتثال الحرجة؟",
        variations_en=[
            "Critical compliance issues",
            "Severe compliance failures",
            "Major non-compliance events"
        ],
        variations_ar=["مشاكل الامتثال الحرجة", "فشل الامتثال الشديد"],
        keywords_en=["critical", "failures", "severe", "major"],
        keywords_ar=["حرج", "فشل", "شديد", "كبير"],
        sql="""
            SELECT COUNT(*) as critical_failures,
                   COUNT(DISTINCT e.LocationID) as affected_locations
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Score < 50 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_005",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "CATEGORY"],
        question_en="What is the compliance rate by violation category?",
        question_ar="ما معدل الامتثال حسب فئة المخالفة؟",
        variations_en=[
            "Compliance by category",
            "Category-wise compliance",
            "Compliance breakdown by type"
        ],
        variations_ar=["الامتثال حسب الفئة", "تقسيم الامتثال"],
        keywords_en=["compliance", "category", "type", "breakdown"],
        keywords_ar=["امتثال", "فئة", "نوع", "تقسيم"],
        sql="""
            SELECT vc.Name as category,
                   COUNT(DISTINCT e.Id) as total_inspections,
                   COUNT(CASE WHEN e.Score >= 80 THEN 1 END) as compliant_count,
                   CAST(COUNT(CASE WHEN e.Score >= 80 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM ViolationCategory vc
            LEFT JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            LEFT JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            LEFT JOIN Event e ON ev.EventId = e.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY compliance_rate ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_006",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "FIRST_TIME"],
        question_en="What is the first-time compliance rate?",
        question_ar="ما معدل الامتثال من المرة الأولى؟",
        variations_en=[
            "First inspection pass rate",
            "Initial compliance rate",
            "Pass rate on first try"
        ],
        variations_ar=["معدل النجاح الأول", "الامتثال من أول فحص"],
        keywords_en=["first", "time", "initial", "pass"],
        keywords_ar=["أول", "مرة", "أولي", "نجاح"],
        sql="""
            WITH FirstInspections AS (
                SELECT e.*, ROW_NUMBER() OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as rn
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT COUNT(CASE WHEN Score >= 80 THEN 1 END) as passed_first_time,
                   COUNT(*) as total_first_inspections,
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
        id="KPI_ADV_COMP_007",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "REPEAT"],
        question_en="How many repeat violations occurred?",
        question_ar="كم عدد المخالفات المتكررة؟",
        variations_en=[
            "Recurring violations",
            "Repeat offenses",
            "Violations that happened again"
        ],
        variations_ar=["المخالفات المتكررة", "التكرارات"],
        keywords_en=["repeat", "recurring", "again", "multiple"],
        keywords_ar=["متكرر", "تكرار", "مرة أخرى"],
        sql="""
            SELECT vt.Name as violation_type, COUNT(*) as occurrence_count,
                   COUNT(DISTINCT e.LocationID) as locations_affected
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            HAVING COUNT(*) > 1
            ORDER BY occurrence_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_008",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "TARGET"],
        question_en="Are we on track to meet our compliance targets?",
        question_ar="هل نحن على المسار الصحيح لتحقيق أهداف الامتثال؟",
        variations_en=[
            "Compliance target progress",
            "Meeting compliance goals",
            "Target achievement status"
        ],
        variations_ar=["تقدم نحو الهدف", "تحقيق أهداف الامتثال"],
        keywords_en=["target", "track", "goals", "meeting"],
        keywords_ar=["هدف", "مسار", "تحقيق"],
        sql="""
            SELECT 
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as current_rate,
                85.0 as target_rate,
                CASE WHEN SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 85 THEN 'On Track' ELSE 'Behind' END as status
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_009",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "GAP"],
        question_en="What is the compliance gap between best and worst locations?",
        question_ar="ما فجوة الامتثال بين أفضل وأسوأ المواقع؟",
        variations_en=[
            "Compliance variance",
            "Best vs worst compliance",
            "Compliance spread"
        ],
        variations_ar=["تباين الامتثال", "الفجوة في الامتثال"],
        keywords_en=["gap", "variance", "best", "worst", "spread"],
        keywords_ar=["فجوة", "تباين", "أفضل", "أسوأ"],
        sql="""
            SELECT 
                MAX(avg_score) as best_score,
                MIN(avg_score) as worst_score,
                MAX(avg_score) - MIN(avg_score) as compliance_gap,
                AVG(avg_score) as average_score
            FROM (
                SELECT l.Id, AVG(e.Score) as avg_score
                FROM Location l JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
            ) loc_scores
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_ADV_COMP_010",
        category=QuestionCategory.KPI,
        subcategory="advanced_compliance",
        intent=["COMPLIANCE", "RECOVERY"],
        question_en="What is the compliance recovery rate after violations?",
        question_ar="ما معدل استعادة الامتثال بعد المخالفات؟",
        variations_en=[
            "Recovery after violation",
            "Bounce back rate",
            "Compliance restoration rate"
        ],
        variations_ar=["الاستعادة بعد المخالفة", "معدل التعافي"],
        keywords_en=["recovery", "after", "bounce", "restoration"],
        keywords_ar=["استعادة", "بعد", "تعافي"],
        sql="""
            WITH ViolationEvents AS (
                SELECT e.LocationID, e.SubmitionDate, e.Score,
                       LEAD(e.Score) OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as next_score
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year} AND e.Score < 80
            )
            SELECT COUNT(CASE WHEN next_score >= 80 THEN 1 END) as recovered,
                   COUNT(*) as total_violations,
                   CAST(COUNT(CASE WHEN next_score >= 80 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as recovery_rate
            FROM ViolationEvents WHERE next_score IS NOT NULL
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.ADVANCED
    ),
]

# ============================================================================
# OPERATIONAL KPIs (10 questions)
# ============================================================================

OPERATIONAL_QUESTIONS = [
    QuestionTemplate(
        id="KPI_OPS_001",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["INSPECTION", "FREQUENCY"],
        question_en="What is the average inspection frequency per location?",
        question_ar="ما متوسط تكرار الفحص لكل موقع؟",
        variations_en=[
            "How often are locations inspected?",
            "Inspection frequency",
            "Average inspections per site"
        ],
        variations_ar=["كم مرة يتم فحص المواقع؟", "تكرار الفحص"],
        keywords_en=["frequency", "often", "average", "per location"],
        keywords_ar=["تكرار", "كم مرة", "متوسط", "لكل موقع"],
        sql="""
            SELECT AVG(inspection_count) as avg_inspections_per_location,
                   MIN(inspection_count) as min_inspections,
                   MAX(inspection_count) as max_inspections
            FROM (
                SELECT l.Id, COUNT(e.Id) as inspection_count
                FROM Location l LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
            ) loc_counts
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_OPS_002",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["INSPECTION", "COVERAGE"],
        question_en="What percentage of locations have been inspected?",
        question_ar="ما نسبة المواقع التي تم فحصها؟",
        variations_en=[
            "Location coverage rate",
            "Inspection coverage",
            "How many locations inspected?"
        ],
        variations_ar=["نسبة تغطية المواقع", "تغطية الفحص"],
        keywords_en=["coverage", "percentage", "inspected", "locations"],
        keywords_ar=["تغطية", "نسبة", "فحص", "مواقع"],
        sql="""
            SELECT 
                (SELECT COUNT(DISTINCT LocationID) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as inspected_locations,
                (SELECT COUNT(*) FROM Location WHERE IsDeleted = 0) as total_locations,
                CAST((SELECT COUNT(DISTINCT LocationID) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) * 100.0 / 
                     NULLIF((SELECT COUNT(*) FROM Location WHERE IsDeleted = 0), 0) AS DECIMAL(5,2)) as coverage_rate
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_OPS_003",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["INSPECTOR", "UTILIZATION"],
        question_en="What is the inspector utilization rate?",
        question_ar="ما معدل استخدام المفتشين؟",
        variations_en=[
            "Inspector workload",
            "How busy are inspectors?",
            "Inspector capacity usage"
        ],
        variations_ar=["حمل عمل المفتشين", "استخدام المفتشين"],
        keywords_en=["utilization", "workload", "busy", "capacity"],
        keywords_ar=["استخدام", "حمل عمل", "طاقة"],
        sql="""
            SELECT u.Name as inspector, COUNT(e.Id) as inspections_done,
                   CAST(COUNT(e.Id) * 100.0 / NULLIF(MAX(target.monthly_target), 0) AS DECIMAL(5,2)) as utilization_pct
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            CROSS JOIN (SELECT 50 as monthly_target) target
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY inspections_done DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_OPS_004",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["BACKLOG", "PENDING"],
        question_en="How many inspections are overdue?",
        question_ar="كم عدد الفحوصات المتأخرة؟",
        variations_en=[
            "Overdue inspections",
            "Inspection backlog",
            "Pending inspections"
        ],
        variations_ar=["الفحوصات المتأخرة", "الفحوصات المعلقة"],
        keywords_en=["overdue", "backlog", "pending", "late"],
        keywords_ar=["متأخر", "معلق", "تأخير"],
        sql="""
            SELECT COUNT(*) as locations_needing_inspection
            FROM Location l
            WHERE l.IsDeleted = 0
            AND NOT EXISTS (
                SELECT 1 FROM Event e 
                WHERE e.LocationID = l.Id AND e.IsDeleted = 0 
                AND e.SubmitionDate >= DATEADD(month, -1, GETDATE())
            )
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_OPS_005",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["THROUGHPUT", "DAILY"],
        question_en="What is the daily inspection throughput?",
        question_ar="ما معدل الفحوصات اليومي؟",
        variations_en=[
            "Daily inspections",
            "Inspections per day",
            "Daily throughput"
        ],
        variations_ar=["الفحوصات اليومية", "معدل يومي"],
        keywords_en=["daily", "throughput", "per day"],
        keywords_ar=["يومي", "معدل", "في اليوم"],
        sql="""
            SELECT CAST(e.SubmitionDate AS DATE) as date,
                   COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CAST(e.SubmitionDate AS DATE)
            ORDER BY date DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_OPS_006",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["PEAK", "HOURS"],
        question_en="What are the peak inspection hours?",
        question_ar="ما هي ساعات الذروة للفحوصات؟",
        variations_en=[
            "Busiest inspection times",
            "Peak hours",
            "When are most inspections done?"
        ],
        variations_ar=["أوقات الذروة", "ساعات الانشغال"],
        keywords_en=["peak", "hours", "busiest", "times"],
        keywords_ar=["ذروة", "ساعات", "أوقات"],
        sql="""
            SELECT DATEPART(HOUR, e.SubmitionDate) as hour,
                   COUNT(*) as inspection_count
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(HOUR, e.SubmitionDate)
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_OPS_007",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["WEEKEND", "ACTIVITY"],
        question_en="How many inspections occur on weekends?",
        question_ar="كم عدد الفحوصات في عطلة نهاية الأسبوع؟",
        variations_en=[
            "Weekend inspections",
            "Saturday Sunday inspections",
            "Weekend activity"
        ],
        variations_ar=["فحوصات عطلة الأسبوع", "فحوصات السبت والأحد"],
        keywords_en=["weekend", "saturday", "sunday"],
        keywords_ar=["عطلة", "سبت", "أحد"],
        sql="""
            SELECT 
                CASE WHEN DATEPART(WEEKDAY, e.SubmitionDate) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END as day_type,
                COUNT(*) as inspection_count
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN DATEPART(WEEKDAY, e.SubmitionDate) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_OPS_008",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["INSPECTOR", "PRODUCTIVITY"],
        question_en="What is the average inspections per inspector per day?",
        question_ar="ما متوسط الفحوصات لكل مفتش في اليوم؟",
        variations_en=[
            "Inspector daily productivity",
            "Inspections per person per day",
            "Daily inspector output"
        ],
        variations_ar=["إنتاجية المفتش اليومية", "فحوصات المفتش اليومية"],
        keywords_en=["per inspector", "per day", "productivity"],
        keywords_ar=["لكل مفتش", "في اليوم", "إنتاجية"],
        sql="""
            SELECT AVG(daily_count) as avg_inspections_per_day
            FROM (
                SELECT e.ReporterID, CAST(e.SubmitionDate AS DATE) as date, COUNT(*) as daily_count
                FROM Event e
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY e.ReporterID, CAST(e.SubmitionDate AS DATE)
            ) daily_stats
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_OPS_009",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["REINSPECTION", "RATE"],
        question_en="What is the reinspection rate?",
        question_ar="ما معدل إعادة الفحص؟",
        variations_en=[
            "How many reinspections?",
            "Reinspection frequency",
            "Follow-up inspection rate"
        ],
        variations_ar=["كم عدد إعادة الفحوصات؟", "معدل المتابعة"],
        keywords_en=["reinspection", "follow-up", "again"],
        keywords_ar=["إعادة فحص", "متابعة"],
        sql="""
            SELECT 
                COUNT(CASE WHEN inspection_num > 1 THEN 1 END) as reinspections,
                COUNT(*) as total_inspections,
                CAST(COUNT(CASE WHEN inspection_num > 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as reinspection_rate
            FROM (
                SELECT e.*, ROW_NUMBER() OVER (PARTITION BY e.LocationID, FORMAT(e.SubmitionDate, 'yyyy-MM') ORDER BY e.SubmitionDate) as inspection_num
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            ) numbered
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_OPS_010",
        category=QuestionCategory.KPI,
        subcategory="operational",
        intent=["EFFICIENCY", "SCORE"],
        question_en="What is the overall operational efficiency score?",
        question_ar="ما هي درجة الكفاءة التشغيلية الإجمالية؟",
        variations_en=[
            "Operational efficiency",
            "Efficiency rating",
            "How efficient are operations?"
        ],
        variations_ar=["الكفاءة التشغيلية", "درجة الكفاءة"],
        keywords_en=["efficiency", "operational", "score", "rating"],
        keywords_ar=["كفاءة", "تشغيلي", "درجة"],
        sql="""
            SELECT 
                (SELECT COUNT(*) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as total_inspections,
                (SELECT COUNT(DISTINCT LocationID) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as locations_covered,
                (SELECT COUNT(DISTINCT ReporterID) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as active_inspectors,
                CAST((SELECT AVG(Score) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) AS DECIMAL(5,2)) as avg_score
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# SAFETY & RISK KPIs (10 questions)
# ============================================================================

SAFETY_RISK_QUESTIONS = [
    QuestionTemplate(
        id="KPI_SAFE_001",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["SAFETY", "VIOLATIONS"],
        question_en="How many safety-related violations occurred?",
        question_ar="كم عدد المخالفات المتعلقة بالسلامة؟",
        variations_en=[
            "Safety violations count",
            "Safety issues",
            "Safety-related problems"
        ],
        variations_ar=["مخالفات السلامة", "مشاكل السلامة"],
        keywords_en=["safety", "violations", "issues"],
        keywords_ar=["سلامة", "مخالفات", "مشاكل"],
        sql="""
            SELECT COUNT(ev.Id) as safety_violations
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN ViolationCategory vc ON vt.ViolationCategoryId = vc.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            AND (vc.Name LIKE '%safety%' OR vc.Name LIKE '%hazard%' OR vt.Name LIKE '%safety%')
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_SAFE_002",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["HIGH", "RISK", "LOCATIONS"],
        question_en="How many high-risk locations do we have?",
        question_ar="كم عدد المواقع عالية المخاطر لدينا؟",
        variations_en=[
            "High risk locations count",
            "Risky locations",
            "Dangerous sites"
        ],
        variations_ar=["المواقع عالية المخاطر", "المواقع الخطرة"],
        keywords_en=["high", "risk", "locations", "dangerous"],
        keywords_ar=["عالي", "مخاطر", "مواقع", "خطر"],
        sql="""
            SELECT COUNT(*) as high_risk_locations
            FROM (
                SELECT l.Id
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
                HAVING AVG(e.Score) < 60
            ) risky
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_SAFE_003",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["RISK", "SCORE", "AVERAGE"],
        question_en="What is the average risk score across all locations?",
        question_ar="ما متوسط درجة المخاطر لجميع المواقع؟",
        variations_en=[
            "Average risk score",
            "Overall risk level",
            "Risk assessment average"
        ],
        variations_ar=["متوسط درجة المخاطر", "مستوى المخاطر العام"],
        keywords_en=["average", "risk", "score", "level"],
        keywords_ar=["متوسط", "مخاطر", "درجة", "مستوى"],
        sql="""
            SELECT 
                100 - CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_risk_score,
                CASE 
                    WHEN AVG(e.Score) >= 80 THEN 'Low Risk'
                    WHEN AVG(e.Score) >= 60 THEN 'Medium Risk'
                    ELSE 'High Risk'
                END as risk_category
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_SAFE_004",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["CRITICAL", "VIOLATIONS", "COUNT"],
        question_en="How many critical violations need immediate attention?",
        question_ar="كم عدد المخالفات الحرجة التي تحتاج اهتماماً فورياً؟",
        variations_en=[
            "Critical violations",
            "Urgent issues",
            "Immediate attention needed"
        ],
        variations_ar=["المخالفات الحرجة", "المشاكل العاجلة"],
        keywords_en=["critical", "urgent", "immediate", "attention"],
        keywords_ar=["حرج", "عاجل", "فوري", "اهتمام"],
        sql="""
            SELECT COUNT(ev.Id) as critical_violations,
                   COUNT(DISTINCT e.LocationID) as affected_locations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND e.Score < 50 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_SAFE_005",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["RISK", "TREND"],
        question_en="Is the overall risk level increasing or decreasing?",
        question_ar="هل مستوى المخاطر العام يزداد أم ينخفض؟",
        variations_en=[
            "Risk trend",
            "Risk direction",
            "Is risk going up or down?"
        ],
        variations_ar=["اتجاه المخاطر", "هل المخاطر تزداد؟"],
        keywords_en=["trend", "increasing", "decreasing", "direction"],
        keywords_ar=["اتجاه", "يزداد", "ينخفض"],
        sql="""
            SELECT FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                   100 - CAST(AVG(e.Score) AS DECIMAL(5,2)) as risk_score,
                   COUNT(ev.Id) as violation_count
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
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_SAFE_006",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["RISK", "DISTRIBUTION"],
        question_en="What is the distribution of risk levels?",
        question_ar="ما توزيع مستويات المخاطر؟",
        variations_en=[
            "Risk level breakdown",
            "Risk categories distribution",
            "How are risks distributed?"
        ],
        variations_ar=["توزيع المخاطر", "تقسيم مستويات المخاطر"],
        keywords_en=["distribution", "breakdown", "levels"],
        keywords_ar=["توزيع", "تقسيم", "مستويات"],
        sql="""
            SELECT 
                CASE 
                    WHEN avg_score >= 80 THEN 'Low Risk'
                    WHEN avg_score >= 60 THEN 'Medium Risk'
                    ELSE 'High Risk'
                END as risk_level,
                COUNT(*) as location_count
            FROM (
                SELECT l.Id, AVG(e.Score) as avg_score
                FROM Location l JOIN Event e ON e.LocationID = l.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
            ) scores
            GROUP BY CASE WHEN avg_score >= 80 THEN 'Low Risk' WHEN avg_score >= 60 THEN 'Medium Risk' ELSE 'High Risk' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_SAFE_007",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["RISK", "MITIGATION"],
        question_en="How many risks have been mitigated?",
        question_ar="كم عدد المخاطر التي تم تخفيفها؟",
        variations_en=[
            "Mitigated risks",
            "Resolved risk issues",
            "Risk reduction"
        ],
        variations_ar=["المخاطر المخففة", "المخاطر المحلولة"],
        keywords_en=["mitigated", "resolved", "reduction"],
        keywords_ar=["مخفف", "محلول", "تخفيف"],
        sql="""
            WITH RiskSequence AS (
                SELECT e.LocationID, e.Score, e.SubmitionDate,
                       LAG(e.Score) OVER (PARTITION BY e.LocationID ORDER BY e.SubmitionDate) as prev_score
                FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            )
            SELECT COUNT(CASE WHEN Score >= 80 AND prev_score < 80 THEN 1 END) as risks_mitigated
            FROM RiskSequence WHERE prev_score IS NOT NULL
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="KPI_SAFE_008",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["HERITAGE", "PROTECTION"],
        question_en="What is the heritage protection compliance rate?",
        question_ar="ما معدل الامتثال لحماية التراث؟",
        variations_en=[
            "Heritage compliance",
            "Cultural site protection",
            "Heritage preservation rate"
        ],
        variations_ar=["امتثال حماية التراث", "حماية المواقع الثقافية"],
        keywords_en=["heritage", "protection", "cultural", "preservation"],
        keywords_ar=["تراث", "حماية", "ثقافي", "حفظ"],
        sql="""
            SELECT 
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as heritage_compliance_rate
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_SAFE_009",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["INCIDENT", "FREE", "DAYS"],
        question_en="How many incident-free days have we achieved?",
        question_ar="كم يوماً مضى بدون حوادث؟",
        variations_en=[
            "Days without incidents",
            "Incident-free streak",
            "Safe days count"
        ],
        variations_ar=["أيام بدون حوادث", "سلسلة الأيام الآمنة"],
        keywords_en=["incident-free", "days", "streak", "safe"],
        keywords_ar=["بدون حوادث", "أيام", "آمن"],
        sql="""
            SELECT DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_since_last_critical
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Score < 50
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_SAFE_010",
        category=QuestionCategory.KPI,
        subcategory="safety",
        intent=["VIOLATION", "SEVERITY"],
        question_en="What is the average violation severity?",
        question_ar="ما متوسط شدة المخالفات؟",
        variations_en=[
            "Violation severity average",
            "How severe are violations?",
            "Average violation impact"
        ],
        variations_ar=["متوسط شدة المخالفات", "مدى خطورة المخالفات"],
        keywords_en=["severity", "average", "impact", "serious"],
        keywords_ar=["شدة", "متوسط", "تأثير", "خطورة"],
        sql="""
            SELECT AVG(ev.Value) as avg_violation_value,
                   COUNT(CASE WHEN ev.Value > 100 THEN 1 END) as high_severity_count,
                   COUNT(*) as total_violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# MANAGEMENT DASHBOARD KPIs (10 questions)
# ============================================================================

MANAGEMENT_QUESTIONS = [
    QuestionTemplate(
        id="KPI_MGMT_001",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["EXECUTIVE", "SUMMARY"],
        question_en="Give me an executive summary of performance",
        question_ar="أعطني ملخصاً تنفيذياً للأداء",
        variations_en=[
            "Executive overview",
            "Management summary",
            "High-level performance summary"
        ],
        variations_ar=["ملخص تنفيذي", "نظرة عامة للإدارة"],
        keywords_en=["executive", "summary", "overview", "management"],
        keywords_ar=["تنفيذي", "ملخص", "نظرة عامة", "إدارة"],
        sql="""
            SELECT 
                (SELECT COUNT(*) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as total_inspections,
                (SELECT CAST(AVG(Score) AS DECIMAL(5,2)) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as avg_score,
                (SELECT CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}) as compliance_rate,
                (SELECT COUNT(*) FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}) as total_violations
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_MGMT_002",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["MONTHLY", "REPORT"],
        question_en="Generate the monthly performance report",
        question_ar="أنشئ تقرير الأداء الشهري",
        variations_en=[
            "Monthly report",
            "This month's performance",
            "Monthly metrics"
        ],
        variations_ar=["التقرير الشهري", "أداء هذا الشهر"],
        keywords_en=["monthly", "report", "performance"],
        keywords_ar=["شهري", "تقرير", "أداء"],
        sql="""
            SELECT FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                   COUNT(*) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate,
                   COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_MGMT_003",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["YTD", "PERFORMANCE"],
        question_en="What is our year-to-date performance?",
        question_ar="ما هو أداؤنا منذ بداية العام؟",
        variations_en=[
            "YTD performance",
            "Year to date metrics",
            "Performance since January"
        ],
        variations_ar=["الأداء منذ بداية العام", "مقاييس السنة حتى الآن"],
        keywords_en=["ytd", "year-to-date", "since january"],
        keywords_ar=["منذ بداية العام", "حتى الآن"],
        sql="""
            SELECT 
                COUNT(*) as ytd_inspections,
                CAST(AVG(Score) AS DECIMAL(5,2)) as ytd_avg_score,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as ytd_compliance
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_MGMT_004",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["GOAL", "PROGRESS"],
        question_en="How are we progressing towards our goals?",
        question_ar="كيف نتقدم نحو أهدافنا؟",
        variations_en=[
            "Goal progress",
            "Target achievement",
            "Are we meeting objectives?"
        ],
        variations_ar=["تقدم الأهداف", "تحقيق الأهداف"],
        keywords_en=["goals", "progress", "targets", "objectives"],
        keywords_ar=["أهداف", "تقدم", "غايات"],
        sql="""
            SELECT 
                'Compliance Rate' as metric,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as actual,
                85.0 as target,
                CASE WHEN SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) >= 85 THEN 'Met' ELSE 'Not Met' END as status
            FROM Event e WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_MGMT_005",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["TOP", "ISSUES"],
        question_en="What are the top issues requiring management attention?",
        question_ar="ما هي أهم المشاكل التي تتطلب اهتمام الإدارة؟",
        variations_en=[
            "Priority issues",
            "Critical problems",
            "What needs attention?"
        ],
        variations_ar=["المشاكل ذات الأولوية", "المشاكل الحرجة"],
        keywords_en=["top", "issues", "priority", "attention"],
        keywords_ar=["أهم", "مشاكل", "أولوية", "اهتمام"],
        sql="""
            SELECT TOP 5 vt.Name as issue, COUNT(*) as occurrence_count,
                   SUM(ev.Value) as total_value
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            ORDER BY occurrence_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_MGMT_006",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["RESOURCE", "ALLOCATION"],
        question_en="How are inspection resources being utilized?",
        question_ar="كيف يتم استخدام موارد الفحص؟",
        variations_en=[
            "Resource utilization",
            "Inspector deployment",
            "Resource allocation"
        ],
        variations_ar=["استخدام الموارد", "توزيع المفتشين"],
        keywords_en=["resource", "utilization", "allocation", "deployment"],
        keywords_ar=["موارد", "استخدام", "توزيع"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   COUNT(DISTINCT e.LocationID) as locations_covered,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_MGMT_007",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["BUDGET", "IMPACT"],
        question_en="What is the financial impact of violations?",
        question_ar="ما هو التأثير المالي للمخالفات؟",
        variations_en=[
            "Violation costs",
            "Financial impact",
            "Cost of non-compliance"
        ],
        variations_ar=["تكاليف المخالفات", "التأثير المالي"],
        keywords_en=["financial", "impact", "cost", "budget"],
        keywords_ar=["مالي", "تأثير", "تكلفة", "ميزانية"],
        sql="""
            SELECT SUM(ev.Value) as total_violation_value,
                   AVG(ev.Value) as avg_violation_value,
                   COUNT(*) as violation_count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_MGMT_008",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["BENCHMARK", "COMPARISON"],
        question_en="How do we compare to last year?",
        question_ar="كيف نقارن بالعام الماضي؟",
        variations_en=[
            "Year over year comparison",
            "Last year comparison",
            "YoY performance"
        ],
        variations_ar=["مقارنة بالعام الماضي", "مقارنة سنوية"],
        keywords_en=["compare", "last year", "yoy", "benchmark"],
        keywords_ar=["مقارنة", "العام الماضي", "سنوي"],
        sql="""
            SELECT 
                'Current Year' as period, COUNT(*) as inspections, CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            UNION ALL
            SELECT 
                'Previous Year', COUNT(*), CAST(AVG(Score) AS DECIMAL(5,2))
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year} - 1
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_MGMT_009",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["FORECAST", "NEXT"],
        question_en="What is the projected compliance for next quarter?",
        question_ar="ما هو الامتثال المتوقع للربع القادم؟",
        variations_en=[
            "Next quarter forecast",
            "Projected compliance",
            "Future outlook"
        ],
        variations_ar=["توقعات الربع القادم", "الامتثال المتوقع"],
        keywords_en=["forecast", "projected", "next quarter", "future"],
        keywords_ar=["توقع", "متوقع", "الربع القادم", "مستقبل"],
        sql="""
            SELECT 
                DATEPART(QUARTER, e.SubmitionDate) as quarter,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_rate
            FROM Event e
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY DATEPART(QUARTER, e.SubmitionDate)
            ORDER BY quarter
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_MGMT_010",
        category=QuestionCategory.KPI,
        subcategory="management",
        intent=["ACTION", "ITEMS"],
        question_en="What action items should be prioritized?",
        question_ar="ما بنود العمل التي يجب تحديد أولويتها؟",
        variations_en=[
            "Priority actions",
            "What should we focus on?",
            "Key action items"
        ],
        variations_ar=["الإجراءات ذات الأولوية", "ماذا يجب التركيز عليه؟"],
        keywords_en=["action", "priority", "focus", "items"],
        keywords_ar=["إجراء", "أولوية", "تركيز", "بنود"],
        sql="""
            SELECT TOP 10 l.Name as location, AVG(e.Score) as avg_score,
                   COUNT(ev.Id) as violations, 'Needs Improvement' as action
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING AVG(e.Score) < 70
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# QUALITY METRICS KPIs (10 questions)
# ============================================================================

QUALITY_QUESTIONS = [
    QuestionTemplate(
        id="KPI_QUAL_001",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["QUALITY", "SCORE"],
        question_en="What is the overall quality score?",
        question_ar="ما هي درجة الجودة الإجمالية؟",
        variations_en=["Quality rating", "Overall quality", "Quality metric"],
        variations_ar=["تقييم الجودة", "الجودة الإجمالية"],
        keywords_en=["quality", "score", "rating", "overall"],
        keywords_ar=["جودة", "درجة", "تقييم", "إجمالي"],
        sql="""
            SELECT CAST(AVG(Score) AS DECIMAL(5,2)) as quality_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_QUAL_002",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["DEFECT", "RATE"],
        question_en="What is the defect rate?",
        question_ar="ما هو معدل العيوب؟",
        variations_en=["Defect percentage", "Failure rate", "Error rate"],
        variations_ar=["نسبة العيوب", "معدل الفشل"],
        keywords_en=["defect", "rate", "failure", "error"],
        keywords_ar=["عيوب", "معدل", "فشل", "خطأ"],
        sql="""
            SELECT CAST(SUM(CASE WHEN Score < 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as defect_rate
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_QUAL_003",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["CONSISTENCY", "VARIATION"],
        question_en="How consistent are inspection scores?",
        question_ar="ما مدى اتساق درجات الفحص؟",
        variations_en=["Score consistency", "Variation in scores", "Score stability"],
        variations_ar=["اتساق الدرجات", "تباين الدرجات"],
        keywords_en=["consistent", "variation", "stability", "deviation"],
        keywords_ar=["اتساق", "تباين", "استقرار"],
        sql="""
            SELECT CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                   CAST(STDEV(Score) AS DECIMAL(5,2)) as score_std_dev,
                   MAX(Score) - MIN(Score) as score_range
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_QUAL_004",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["EXCELLENCE", "COUNT"],
        question_en="How many inspections achieved excellence (90+)?",
        question_ar="كم عدد الفحوصات التي حققت التميز (90+)؟",
        variations_en=["Excellent inspections", "90+ scores", "Excellence count"],
        variations_ar=["الفحوصات المتميزة", "درجات 90+"],
        keywords_en=["excellence", "90", "outstanding", "excellent"],
        keywords_ar=["تميز", "90", "متميز"],
        sql="""
            SELECT COUNT(CASE WHEN Score >= 90 THEN 1 END) as excellent_count,
                   COUNT(*) as total,
                   CAST(COUNT(CASE WHEN Score >= 90 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as excellence_rate
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_QUAL_005",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["QUALITY", "TREND"],
        question_en="Is quality improving over time?",
        question_ar="هل الجودة تتحسن مع الوقت؟",
        variations_en=["Quality trend", "Quality improvement", "Quality over time"],
        variations_ar=["اتجاه الجودة", "تحسن الجودة"],
        keywords_en=["improving", "trend", "over time", "quality"],
        keywords_ar=["تحسن", "اتجاه", "مع الوقت", "جودة"],
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
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_QUAL_006",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["ZERO", "DEFECT"],
        question_en="How many locations have zero defects?",
        question_ar="كم عدد المواقع بدون عيوب؟",
        variations_en=["Zero defect locations", "Perfect locations", "Defect-free sites"],
        variations_ar=["مواقع بدون عيوب", "مواقع مثالية"],
        keywords_en=["zero", "defect", "perfect", "defect-free"],
        keywords_ar=["صفر", "عيوب", "مثالي"],
        sql="""
            SELECT COUNT(*) as zero_defect_locations
            FROM (
                SELECT l.Id
                FROM Location l
                JOIN Event e ON e.LocationID = l.Id
                LEFT JOIN EventViolation ev ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
                GROUP BY l.Id
                HAVING COUNT(ev.Id) = 0
            ) perfect
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_QUAL_007",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["INSPECTOR", "QUALITY"],
        question_en="Which inspectors have the highest quality scores?",
        question_ar="أي المفتشين لديهم أعلى درجات جودة؟",
        variations_en=["Top quality inspectors", "Best inspector scores", "Inspector quality ranking"],
        variations_ar=["أفضل المفتشين جودة", "ترتيب جودة المفتشين"],
        keywords_en=["inspector", "quality", "highest", "best"],
        keywords_ar=["مفتش", "جودة", "أعلى", "أفضل"],
        sql="""
            SELECT TOP 10 u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(e.Id) >= 5
            ORDER BY avg_score DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_QUAL_008",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["SCORE", "DISTRIBUTION"],
        question_en="What is the distribution of scores?",
        question_ar="ما هو توزيع الدرجات؟",
        variations_en=["Score distribution", "Score breakdown", "How are scores distributed?"],
        variations_ar=["توزيع الدرجات", "تقسيم الدرجات"],
        keywords_en=["distribution", "breakdown", "scores"],
        keywords_ar=["توزيع", "تقسيم", "درجات"],
        sql="""
            SELECT 
                CASE 
                    WHEN Score >= 90 THEN '90-100 (Excellent)'
                    WHEN Score >= 80 THEN '80-89 (Good)'
                    WHEN Score >= 70 THEN '70-79 (Fair)'
                    WHEN Score >= 60 THEN '60-69 (Poor)'
                    ELSE 'Below 60 (Critical)'
                END as score_range,
                COUNT(*) as count
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
            GROUP BY CASE WHEN Score >= 90 THEN '90-100 (Excellent)' WHEN Score >= 80 THEN '80-89 (Good)' WHEN Score >= 70 THEN '70-79 (Fair)' WHEN Score >= 60 THEN '60-69 (Poor)' ELSE 'Below 60 (Critical)' END
            ORDER BY MIN(Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="KPI_QUAL_009",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["MEDIAN", "SCORE"],
        question_en="What is the median inspection score?",
        question_ar="ما هو متوسط درجة الفحص؟",
        variations_en=["Median score", "Middle score", "Score median"],
        variations_ar=["الوسيط", "الدرجة المتوسطة"],
        keywords_en=["median", "middle", "score"],
        keywords_ar=["وسيط", "متوسط", "درجة"],
        sql="""
            SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Score) OVER () as median_score
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="KPI_QUAL_010",
        category=QuestionCategory.KPI,
        subcategory="quality",
        intent=["QUALITY", "INDEX"],
        question_en="What is our overall quality index?",
        question_ar="ما هو مؤشر الجودة الإجمالي لدينا؟",
        variations_en=["Quality index", "QI score", "Quality indicator"],
        variations_ar=["مؤشر الجودة", "درجة الجودة"],
        keywords_en=["quality", "index", "indicator", "qi"],
        keywords_ar=["جودة", "مؤشر", "دليل"],
        sql="""
            SELECT 
                CAST(AVG(Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as compliance_pct,
                CAST((AVG(Score) + SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)) / 2 AS DECIMAL(5,2)) as quality_index
            FROM Event WHERE IsDeleted = 0 AND YEAR(SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]


# ============================================================================
# REGISTER ALL EXTENDED KPI QUESTIONS
# ============================================================================

ALL_EXTENDED_KPI_QUESTIONS = (
    ADVANCED_COMPLIANCE_QUESTIONS +
    OPERATIONAL_QUESTIONS +
    SAFETY_RISK_QUESTIONS +
    MANAGEMENT_QUESTIONS +
    QUALITY_QUESTIONS
)

# Register all questions
registry.register_many(ALL_EXTENDED_KPI_QUESTIONS)

print(f"Extended KPI Questions loaded: {len(ALL_EXTENDED_KPI_QUESTIONS)} templates")
