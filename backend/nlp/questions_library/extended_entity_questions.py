"""
Extended Entity Questions Library
==================================
50+ additional entity-related questions covering inspectors, locations,
neighborhoods, violations, and organizational hierarchy.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# INSPECTOR ENTITY QUESTIONS (15 questions)
# ============================================================================

INSPECTOR_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_INSP_001",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "LIST"],
        question_en="List all active inspectors",
        question_ar="اعرض جميع المفتشين النشطين",
        variations_en=["Show all inspectors", "Who are our inspectors?", "All inspectors list"],
        variations_ar=["أظهر جميع المفتشين", "من هم المفتشون؟"],
        keywords_en=["inspector", "list", "all", "active"],
        keywords_ar=["مفتش", "قائمة", "جميع", "نشط"],
        sql="""
            SELECT DISTINCT u.Id, u.Name as inspector_name
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            ORDER BY u.Name
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_002",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "PROFILE"],
        question_en="Show me the profile of inspector {inspector_name}",
        question_ar="أظهر لي ملف المفتش {inspector_name}",
        variations_en=["Inspector profile", "Details about inspector", "Inspector information"],
        variations_ar=["ملف المفتش", "تفاصيل المفتش"],
        keywords_en=["profile", "inspector", "details", "information"],
        keywords_ar=["ملف", "مفتش", "تفاصيل", "معلومات"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as total_inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   MIN(e.SubmitionDate) as first_inspection,
                   MAX(e.SubmitionDate) as last_inspection,
                   COUNT(DISTINCT e.LocationID) as locations_inspected
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE u.Name LIKE '%{inspector_name}%' AND e.IsDeleted = 0
            GROUP BY u.Id, u.Name
        """,
        parameters={"inspector_name": str, "year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_003",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "TOP"],
        question_en="Who is the top performing inspector?",
        question_ar="من هو المفتش الأفضل أداءً؟",
        variations_en=["Best inspector", "Top inspector", "Highest performing inspector"],
        variations_ar=["أفضل مفتش", "المفتش الأعلى"],
        keywords_en=["top", "best", "inspector", "performing"],
        keywords_ar=["أفضل", "أعلى", "مفتش", "أداء"],
        sql="""
            SELECT TOP 1 u.Name as inspector,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            HAVING COUNT(e.Id) >= 5
            ORDER BY AVG(e.Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_004",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "WORKLOAD"],
        question_en="What is the workload of each inspector?",
        question_ar="ما هو حمل العمل لكل مفتش؟",
        variations_en=["Inspector workloads", "How busy is each inspector?", "Workload by inspector"],
        variations_ar=["حمل عمل المفتشين", "انشغال كل مفتش"],
        keywords_en=["workload", "inspector", "busy", "each"],
        keywords_ar=["حمل عمل", "مفتش", "مشغول", "كل"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as total_inspections,
                   COUNT(DISTINCT e.LocationID) as unique_locations,
                   COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)) as active_days
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY total_inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_005",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "HISTORY"],
        question_en="What is the inspection history of inspector {inspector_name}?",
        question_ar="ما هو سجل فحوصات المفتش {inspector_name}؟",
        variations_en=["Inspector history", "Past inspections by inspector", "Inspector records"],
        variations_ar=["سجل المفتش", "الفحوصات السابقة للمفتش"],
        keywords_en=["history", "past", "inspector", "records"],
        keywords_ar=["سجل", "سابق", "مفتش", "تاريخ"],
        sql="""
            SELECT e.Id, l.Name as location, e.Score, e.SubmitionDate
            FROM Event e
            JOIN [User] u ON e.ReporterID = u.Id
            JOIN Location l ON e.LocationID = l.Id
            WHERE u.Name LIKE '%{inspector_name}%' AND e.IsDeleted = 0
            ORDER BY e.SubmitionDate DESC
        """,
        parameters={"inspector_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_006",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "AREAS"],
        question_en="Which areas does each inspector cover?",
        question_ar="أي المناطق يغطيها كل مفتش؟",
        variations_en=["Inspector coverage areas", "Areas by inspector", "Inspector territories"],
        variations_ar=["مناطق تغطية المفتشين", "المناطق حسب المفتش"],
        keywords_en=["areas", "cover", "inspector", "territory"],
        keywords_ar=["مناطق", "تغطية", "مفتش", "منطقة"],
        sql="""
            SELECT u.Name as inspector, n.Name as neighborhood,
                   COUNT(e.Id) as inspections
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            JOIN Location l ON e.LocationID = l.Id
            JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, n.Id, n.Name
            ORDER BY u.Name, inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_007",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "CONSISTENCY"],
        question_en="Which inspectors are most consistent?",
        question_ar="أي المفتشين الأكثر اتساقاً؟",
        variations_en=["Most consistent inspectors", "Inspector consistency", "Reliable inspectors"],
        variations_ar=["المفتشون الأكثر اتساقاً", "اتساق المفتشين"],
        keywords_en=["consistent", "reliable", "stable", "inspector"],
        keywords_ar=["متسق", "موثوق", "مستقر", "مفتش"],
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
            ORDER BY STDEV(e.Score) ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_008",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "NEW"],
        question_en="Who are the new inspectors?",
        question_ar="من هم المفتشون الجدد؟",
        variations_en=["New inspectors", "Recently added inspectors", "New team members"],
        variations_ar=["المفتشون الجدد", "المفتشون المضافون حديثاً"],
        keywords_en=["new", "recent", "added", "inspector"],
        keywords_ar=["جديد", "حديث", "مضاف", "مفتش"],
        sql="""
            SELECT u.Name as inspector,
                   MIN(e.SubmitionDate) as first_inspection,
                   COUNT(e.Id) as inspections_so_far,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
            GROUP BY u.Id, u.Name
            HAVING MIN(e.SubmitionDate) >= DATEADD(month, -3, GETDATE())
            ORDER BY MIN(e.SubmitionDate) DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_009",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "INACTIVE"],
        question_en="Which inspectors have been inactive?",
        question_ar="أي المفتشين كانوا غير نشطين؟",
        variations_en=["Inactive inspectors", "Inspectors not working", "Idle inspectors"],
        variations_ar=["المفتشون غير النشطين", "المفتشون الخاملون"],
        keywords_en=["inactive", "idle", "not working", "inspector"],
        keywords_ar=["غير نشط", "خامل", "لا يعمل", "مفتش"],
        sql="""
            SELECT u.Name as inspector,
                   MAX(e.SubmitionDate) as last_inspection,
                   DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_inactive
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
            GROUP BY u.Id, u.Name
            HAVING DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) > 14
            ORDER BY days_inactive DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_010",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "SPECIALTY"],
        question_en="What are the specialties of each inspector?",
        question_ar="ما هي تخصصات كل مفتش؟",
        variations_en=["Inspector specialties", "What does each inspector handle?", "Inspector expertise"],
        variations_ar=["تخصصات المفتشين", "ماذا يعالج كل مفتش؟"],
        keywords_en=["specialty", "expertise", "handle", "inspector"],
        keywords_ar=["تخصص", "خبرة", "معالجة", "مفتش"],
        sql="""
            SELECT u.Name as inspector, vc.Name as category,
                   COUNT(ev.Id) as violations_found
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN ViolationCategory vc ON vt.ViolationCategoryId = vc.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, vc.Id, vc.Name
            ORDER BY u.Name, violations_found DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_011",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "PERFORMANCE", "TREND"],
        question_en="How has inspector performance changed over time?",
        question_ar="كيف تغير أداء المفتشين مع الوقت؟",
        variations_en=["Inspector performance trend", "Performance over time", "Inspector improvement"],
        variations_ar=["اتجاه أداء المفتشين", "الأداء مع الوقت"],
        keywords_en=["performance", "trend", "time", "change"],
        keywords_ar=["أداء", "اتجاه", "وقت", "تغيير"],
        sql="""
            SELECT u.Name as inspector,
                   FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name, FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY u.Name, month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_012",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "COUNT"],
        question_en="How many inspectors do we have?",
        question_ar="كم عدد المفتشين لدينا؟",
        variations_en=["Total inspectors", "Inspector count", "Number of inspectors"],
        variations_ar=["إجمالي المفتشين", "عدد المفتشين"],
        keywords_en=["how many", "count", "total", "inspectors"],
        keywords_ar=["كم", "عدد", "إجمالي", "مفتشين"],
        sql="""
            SELECT COUNT(DISTINCT e.ReporterID) as total_inspectors
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
        id="ENT_INSP_013",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "VIOLATIONS", "FOUND"],
        question_en="How many violations has each inspector found?",
        question_ar="كم عدد المخالفات التي وجدها كل مفتش؟",
        variations_en=["Violations by inspector", "Inspector violation counts", "Who found most violations?"],
        variations_ar=["المخالفات حسب المفتش", "عدد مخالفات المفتش"],
        keywords_en=["violations", "found", "inspector", "count"],
        keywords_ar=["مخالفات", "وجد", "مفتش", "عدد"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(ev.Id) as violations_found,
                   COUNT(DISTINCT e.Id) as inspections
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY violations_found DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_INSP_014",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "DAILY", "AVERAGE"],
        question_en="What is the daily average for each inspector?",
        question_ar="ما هو المتوسط اليومي لكل مفتش؟",
        variations_en=["Daily inspections by inspector", "Average per day per inspector", "Inspector daily rate"],
        variations_ar=["الفحوصات اليومية للمفتش", "المعدل اليومي للمفتش"],
        keywords_en=["daily", "average", "inspector", "per day"],
        keywords_ar=["يومي", "متوسط", "مفتش", "في اليوم"],
        sql="""
            SELECT u.Name as inspector,
                   COUNT(e.Id) as total_inspections,
                   COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)) as active_days,
                   CAST(COUNT(e.Id) * 1.0 / NULLIF(COUNT(DISTINCT CAST(e.SubmitionDate AS DATE)), 0) AS DECIMAL(5,2)) as avg_per_day
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY avg_per_day DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_015",
        category=QuestionCategory.ENTITY,
        subcategory="inspector",
        intent=["INSPECTOR", "RANKING"],
        question_en="Rank all inspectors by performance",
        question_ar="رتب جميع المفتشين حسب الأداء",
        variations_en=["Inspector rankings", "All inspectors ranked", "Performance ranking"],
        variations_ar=["ترتيب المفتشين", "جميع المفتشين مرتبين"],
        keywords_en=["rank", "all", "performance", "inspector"],
        keywords_ar=["ترتيب", "جميع", "أداء", "مفتش"],
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
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# LOCATION ENTITY QUESTIONS (15 questions)
# ============================================================================

LOCATION_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_LOC_001",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "LIST"],
        question_en="List all locations",
        question_ar="اعرض جميع المواقع",
        variations_en=["Show all locations", "All sites", "Location list"],
        variations_ar=["أظهر جميع المواقع", "جميع المواقع"],
        keywords_en=["location", "list", "all", "sites"],
        keywords_ar=["موقع", "قائمة", "جميع", "مواقع"],
        sql="""
            SELECT l.Id, l.Name as location, n.Name as neighborhood
            FROM Location l
            LEFT JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            WHERE l.IsDeleted = 0
            ORDER BY l.Name
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_002",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "DETAILS"],
        question_en="Show details for location {location_name}",
        question_ar="أظهر تفاصيل الموقع {location_name}",
        variations_en=["Location details", "Info about location", "Location profile"],
        variations_ar=["تفاصيل الموقع", "معلومات الموقع"],
        keywords_en=["details", "location", "info", "profile"],
        keywords_ar=["تفاصيل", "موقع", "معلومات", "ملف"],
        sql="""
            SELECT l.Name as location, n.Name as neighborhood,
                   COUNT(e.Id) as total_inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   MIN(e.SubmitionDate) as first_inspection,
                   MAX(e.SubmitionDate) as last_inspection
            FROM Location l
            LEFT JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            WHERE l.Name LIKE '%{location_name}%'
            GROUP BY l.Id, l.Name, n.Id, n.Name
        """,
        parameters={"location_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_003",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "COUNT"],
        question_en="How many locations do we have?",
        question_ar="كم عدد المواقع لدينا؟",
        variations_en=["Total locations", "Location count", "Number of sites"],
        variations_ar=["إجمالي المواقع", "عدد المواقع"],
        keywords_en=["how many", "count", "total", "locations"],
        keywords_ar=["كم", "عدد", "إجمالي", "مواقع"],
        sql="""
            SELECT COUNT(*) as total_locations
            FROM Location WHERE IsDeleted = 0
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_004",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "BEST"],
        question_en="Which locations have the best scores?",
        question_ar="أي المواقع لديها أفضل الدرجات؟",
        variations_en=["Best locations", "Top scoring locations", "Highest rated sites"],
        variations_ar=["أفضل المواقع", "المواقع الأعلى درجة"],
        keywords_en=["best", "top", "highest", "locations"],
        keywords_ar=["أفضل", "أعلى", "مواقع"],
        sql="""
            SELECT TOP 10 l.Name as location,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(e.Id) >= 2
            ORDER BY AVG(e.Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_005",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "WORST"],
        question_en="Which locations have the worst scores?",
        question_ar="أي المواقع لديها أسوأ الدرجات؟",
        variations_en=["Worst locations", "Lowest scoring locations", "Problematic sites"],
        variations_ar=["أسوأ المواقع", "المواقع الأدنى درجة"],
        keywords_en=["worst", "lowest", "problem", "locations"],
        keywords_ar=["أسوأ", "أدنى", "مشكلة", "مواقع"],
        sql="""
            SELECT TOP 10 l.Name as location,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING COUNT(e.Id) >= 2
            ORDER BY AVG(e.Score) ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_006",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "UNINSPECTED"],
        question_en="Which locations haven't been inspected?",
        question_ar="أي المواقع لم يتم فحصها؟",
        variations_en=["Uninspected locations", "Locations without inspections", "Missing inspections"],
        variations_ar=["مواقع غير مفحوصة", "مواقع بدون فحوصات"],
        keywords_en=["uninspected", "without", "missing", "locations"],
        keywords_ar=["غير مفحوص", "بدون", "مفقود", "مواقع"],
        sql="""
            SELECT l.Name as location, n.Name as neighborhood
            FROM Location l
            LEFT JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            WHERE l.IsDeleted = 0 AND e.Id IS NULL
            ORDER BY l.Name
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_007",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "HISTORY"],
        question_en="What is the inspection history of location {location_name}?",
        question_ar="ما هو سجل فحوصات الموقع {location_name}؟",
        variations_en=["Location history", "Past inspections at location", "Location inspection records"],
        variations_ar=["سجل الموقع", "الفحوصات السابقة للموقع"],
        keywords_en=["history", "past", "location", "records"],
        keywords_ar=["سجل", "سابق", "موقع", "تاريخ"],
        sql="""
            SELECT e.Id, e.Score, e.SubmitionDate, u.Name as inspector
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE l.Name LIKE '%{location_name}%' AND e.IsDeleted = 0
            ORDER BY e.SubmitionDate DESC
        """,
        parameters={"location_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_008",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "VIOLATIONS"],
        question_en="What violations occurred at location {location_name}?",
        question_ar="ما المخالفات التي حدثت في الموقع {location_name}؟",
        variations_en=["Location violations", "Violations at site", "Issues at location"],
        variations_ar=["مخالفات الموقع", "المخالفات في الموقع"],
        keywords_en=["violations", "location", "issues", "at"],
        keywords_ar=["مخالفات", "موقع", "مشاكل", "في"],
        sql="""
            SELECT vt.Name as violation_type, COUNT(*) as count
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            JOIN Location l ON e.LocationID = l.Id
            WHERE l.Name LIKE '%{location_name}%' AND e.IsDeleted = 0
            GROUP BY vt.Id, vt.Name
            ORDER BY count DESC
        """,
        parameters={"location_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_009",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "NEIGHBORHOOD"],
        question_en="Which locations are in neighborhood {neighborhood_name}?",
        question_ar="أي المواقع في حي {neighborhood_name}؟",
        variations_en=["Locations in neighborhood", "Sites in area", "Neighborhood locations"],
        variations_ar=["المواقع في الحي", "المواقع في المنطقة"],
        keywords_en=["locations", "neighborhood", "in", "area"],
        keywords_ar=["مواقع", "حي", "في", "منطقة"],
        sql="""
            SELECT l.Name as location,
                   (SELECT COUNT(*) FROM Event e WHERE e.LocationID = l.Id AND e.IsDeleted = 0) as inspections
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            WHERE n.Name LIKE '%{neighborhood_name}%' AND l.IsDeleted = 0
            ORDER BY l.Name
        """,
        parameters={"neighborhood_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_010",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "IMPROVEMENT"],
        question_en="Which locations have improved the most?",
        question_ar="أي المواقع تحسنت أكثر؟",
        variations_en=["Most improved locations", "Location improvements", "Sites getting better"],
        variations_ar=["المواقع الأكثر تحسناً", "تحسينات المواقع"],
        keywords_en=["improved", "most", "better", "locations"],
        keywords_ar=["تحسن", "أكثر", "أفضل", "مواقع"],
        sql="""
            SELECT l.Name as location,
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
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.ADVANCED
    ),
    QuestionTemplate(
        id="ENT_LOC_011",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "FREQUENT"],
        question_en="Which locations are inspected most frequently?",
        question_ar="أي المواقع يتم فحصها بشكل متكرر؟",
        variations_en=["Frequently inspected locations", "Most inspected sites", "High frequency locations"],
        variations_ar=["المواقع الأكثر فحصاً", "المواقع عالية التكرار"],
        keywords_en=["frequent", "most", "inspected", "often"],
        keywords_ar=["متكرر", "أكثر", "فحص", "كثيراً"],
        sql="""
            SELECT TOP 10 l.Name as location,
                   COUNT(e.Id) as inspection_count
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_012",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "NEW"],
        question_en="Which locations are new?",
        question_ar="أي المواقع جديدة؟",
        variations_en=["New locations", "Recently added locations", "New sites"],
        variations_ar=["المواقع الجديدة", "المواقع المضافة حديثاً"],
        keywords_en=["new", "recent", "added", "locations"],
        keywords_ar=["جديد", "حديث", "مضاف", "مواقع"],
        sql="""
            SELECT l.Name as location, n.Name as neighborhood,
                   MIN(e.SubmitionDate) as first_inspection
            FROM Location l
            LEFT JOIN Neighborhood n ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0
            GROUP BY l.Id, l.Name, n.Id, n.Name
            HAVING MIN(e.SubmitionDate) >= DATEADD(month, -3, GETDATE())
            ORDER BY first_inspection DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_013",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "RISK", "HIGH"],
        question_en="Which locations are high risk?",
        question_ar="أي المواقع عالية المخاطر؟",
        variations_en=["High risk locations", "Risky sites", "Dangerous locations"],
        variations_ar=["المواقع عالية المخاطر", "المواقع الخطرة"],
        keywords_en=["high", "risk", "dangerous", "locations"],
        keywords_ar=["عالي", "مخاطر", "خطر", "مواقع"],
        sql="""
            SELECT l.Name as location,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   COUNT(ev.Id) as violations
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
    QuestionTemplate(
        id="ENT_LOC_014",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "OVERDUE"],
        question_en="Which locations are overdue for inspection?",
        question_ar="أي المواقع متأخرة عن الفحص؟",
        variations_en=["Overdue locations", "Locations needing inspection", "Late for inspection"],
        variations_ar=["المواقع المتأخرة", "المواقع التي تحتاج فحص"],
        keywords_en=["overdue", "late", "needing", "inspection"],
        keywords_ar=["متأخر", "تحتاج", "فحص"],
        sql="""
            SELECT l.Name as location,
                   MAX(e.SubmitionDate) as last_inspection,
                   DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) as days_since
            FROM Location l
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            WHERE l.IsDeleted = 0
            GROUP BY l.Id, l.Name
            HAVING DATEDIFF(day, MAX(e.SubmitionDate), GETDATE()) > 30 OR MAX(e.SubmitionDate) IS NULL
            ORDER BY days_since DESC
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_LOC_015",
        category=QuestionCategory.ENTITY,
        subcategory="location",
        intent=["LOCATION", "PERFECT"],
        question_en="Which locations have perfect scores?",
        question_ar="أي المواقع لديها درجات مثالية؟",
        variations_en=["Perfect score locations", "100% compliant locations", "Excellent locations"],
        variations_ar=["مواقع الدرجات المثالية", "مواقع الامتثال الكامل"],
        keywords_en=["perfect", "100", "excellent", "locations"],
        keywords_ar=["مثالي", "100", "ممتاز", "مواقع"],
        sql="""
            SELECT l.Name as location,
                   COUNT(e.Id) as inspections,
                   MIN(e.Score) as min_score
            FROM Location l
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY l.Id, l.Name
            HAVING MIN(e.Score) >= 90
            ORDER BY MIN(e.Score) DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# NEIGHBORHOOD ENTITY QUESTIONS (10 questions)
# ============================================================================

NEIGHBORHOOD_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_NEIGH_001",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "LIST"],
        question_en="List all neighborhoods",
        question_ar="اعرض جميع الأحياء",
        variations_en=["Show all neighborhoods", "All areas", "Neighborhood list"],
        variations_ar=["أظهر جميع الأحياء", "جميع المناطق"],
        keywords_en=["neighborhood", "list", "all", "areas"],
        keywords_ar=["حي", "قائمة", "جميع", "مناطق"],
        sql="""
            SELECT n.Id, n.Name as neighborhood,
                   (SELECT COUNT(*) FROM Location l WHERE l.NeighborhoodID = n.Id AND l.IsDeleted = 0) as location_count
            FROM Neighborhood n
            ORDER BY n.Name
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_NEIGH_002",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "DETAILS"],
        question_en="Show details for neighborhood {neighborhood_name}",
        question_ar="أظهر تفاصيل الحي {neighborhood_name}",
        variations_en=["Neighborhood details", "Info about area", "Neighborhood profile"],
        variations_ar=["تفاصيل الحي", "معلومات المنطقة"],
        keywords_en=["details", "neighborhood", "info", "profile"],
        keywords_ar=["تفاصيل", "حي", "معلومات", "ملف"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(DISTINCT l.Id) as locations,
                   COUNT(e.Id) as total_inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            LEFT JOIN Location l ON l.NeighborhoodID = n.Id AND l.IsDeleted = 0
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            WHERE n.Name LIKE '%{neighborhood_name}%'
            GROUP BY n.Id, n.Name
        """,
        parameters={"neighborhood_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_NEIGH_003",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "BEST"],
        question_en="Which neighborhood has the best compliance?",
        question_ar="أي حي لديه أفضل امتثال؟",
        variations_en=["Best neighborhood", "Top performing area", "Highest rated neighborhood"],
        variations_ar=["أفضل حي", "المنطقة الأعلى أداءً"],
        keywords_en=["best", "neighborhood", "compliance", "top"],
        keywords_ar=["أفضل", "حي", "امتثال", "أعلى"],
        sql="""
            SELECT TOP 5 n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
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
    QuestionTemplate(
        id="ENT_NEIGH_004",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "WORST"],
        question_en="Which neighborhood has the worst compliance?",
        question_ar="أي حي لديه أسوأ امتثال؟",
        variations_en=["Worst neighborhood", "Lowest performing area", "Problem neighborhood"],
        variations_ar=["أسوأ حي", "المنطقة الأدنى أداءً"],
        keywords_en=["worst", "neighborhood", "lowest", "problem"],
        keywords_ar=["أسوأ", "حي", "أدنى", "مشكلة"],
        sql="""
            SELECT TOP 5 n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY avg_score ASC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_NEIGH_005",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "VIOLATIONS"],
        question_en="What violations are common in neighborhood {neighborhood_name}?",
        question_ar="ما المخالفات الشائعة في حي {neighborhood_name}؟",
        variations_en=["Neighborhood violations", "Common issues in area", "Problems in neighborhood"],
        variations_ar=["مخالفات الحي", "المشاكل الشائعة في المنطقة"],
        keywords_en=["violations", "common", "neighborhood", "issues"],
        keywords_ar=["مخالفات", "شائعة", "حي", "مشاكل"],
        sql="""
            SELECT vt.Name as violation_type, COUNT(*) as count
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            WHERE n.Name LIKE '%{neighborhood_name}%' AND e.IsDeleted = 0
            GROUP BY vt.Id, vt.Name
            ORDER BY count DESC
        """,
        parameters={"neighborhood_name": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_NEIGH_006",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "COUNT"],
        question_en="How many neighborhoods do we have?",
        question_ar="كم عدد الأحياء لدينا؟",
        variations_en=["Total neighborhoods", "Neighborhood count", "Number of areas"],
        variations_ar=["إجمالي الأحياء", "عدد الأحياء"],
        keywords_en=["how many", "count", "total", "neighborhoods"],
        keywords_ar=["كم", "عدد", "إجمالي", "أحياء"],
        sql="SELECT COUNT(*) as total_neighborhoods FROM Neighborhood",
        parameters={},
        default_values={},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_NEIGH_007",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "RANKING"],
        question_en="Rank all neighborhoods by compliance",
        question_ar="رتب جميع الأحياء حسب الامتثال",
        variations_en=["Neighborhood rankings", "All neighborhoods ranked", "Compliance ranking by area"],
        variations_ar=["ترتيب الأحياء", "جميع الأحياء مرتبة"],
        keywords_en=["rank", "all", "neighborhoods", "compliance"],
        keywords_ar=["ترتيب", "جميع", "أحياء", "امتثال"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(e.Id) as inspections,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                   RANK() OVER (ORDER BY AVG(e.Score) DESC) as rank
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY rank
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_NEIGH_008",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "COVERAGE"],
        question_en="What is the inspection coverage for each neighborhood?",
        question_ar="ما هي تغطية الفحص لكل حي؟",
        variations_en=["Neighborhood coverage", "Coverage by area", "Inspection coverage"],
        variations_ar=["تغطية الأحياء", "التغطية حسب المنطقة"],
        keywords_en=["coverage", "neighborhood", "inspection", "each"],
        keywords_ar=["تغطية", "حي", "فحص", "كل"],
        sql="""
            SELECT n.Name as neighborhood,
                   COUNT(DISTINCT l.Id) as total_locations,
                   COUNT(DISTINCT e.LocationID) as inspected_locations,
                   CAST(COUNT(DISTINCT e.LocationID) * 100.0 / NULLIF(COUNT(DISTINCT l.Id), 0) AS DECIMAL(5,2)) as coverage_pct
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id AND l.IsDeleted = 0
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name
            ORDER BY coverage_pct DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_NEIGH_009",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "TREND"],
        question_en="What is the performance trend for each neighborhood?",
        question_ar="ما هو اتجاه الأداء لكل حي؟",
        variations_en=["Neighborhood trends", "Area performance over time", "Trend by neighborhood"],
        variations_ar=["اتجاهات الأحياء", "أداء المنطقة مع الوقت"],
        keywords_en=["trend", "performance", "neighborhood", "over time"],
        keywords_ar=["اتجاه", "أداء", "حي", "مع الوقت"],
        sql="""
            SELECT n.Name as neighborhood,
                   FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                   CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY n.Name, month
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_NEIGH_010",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhood",
        intent=["NEIGHBORHOOD", "INSPECTORS"],
        question_en="Which inspectors work in each neighborhood?",
        question_ar="أي المفتشين يعملون في كل حي؟",
        variations_en=["Inspectors by neighborhood", "Who works where?", "Neighborhood inspectors"],
        variations_ar=["المفتشون حسب الحي", "من يعمل أين؟"],
        keywords_en=["inspectors", "neighborhood", "work", "each"],
        keywords_ar=["مفتشون", "حي", "يعمل", "كل"],
        sql="""
            SELECT n.Name as neighborhood, u.Name as inspector,
                   COUNT(e.Id) as inspections
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodID = n.Id
            JOIN Event e ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY n.Id, n.Name, u.Id, u.Name
            ORDER BY n.Name, inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
]

# ============================================================================
# VIOLATION ENTITY QUESTIONS (10 questions)
# ============================================================================

VIOLATION_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_VIOL_001",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "TYPES"],
        question_en="List all violation types",
        question_ar="اعرض جميع أنواع المخالفات",
        variations_en=["Show violation types", "All violations", "Violation type list"],
        variations_ar=["أظهر أنواع المخالفات", "جميع المخالفات"],
        keywords_en=["violation", "types", "list", "all"],
        keywords_ar=["مخالفة", "أنواع", "قائمة", "جميع"],
        sql="""
            SELECT vt.Id, vt.Name as violation_type, vc.Name as category
            FROM ViolationType vt
            LEFT JOIN ViolationCategory vc ON vt.ViolationCategoryId = vc.Id
            ORDER BY vc.Name, vt.Name
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_VIOL_002",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "CATEGORIES"],
        question_en="List all violation categories",
        question_ar="اعرض جميع فئات المخالفات",
        variations_en=["Show categories", "All violation categories", "Category list"],
        variations_ar=["أظهر الفئات", "جميع فئات المخالفات"],
        keywords_en=["categories", "violation", "list", "all"],
        keywords_ar=["فئات", "مخالفة", "قائمة", "جميع"],
        sql="""
            SELECT vc.Id, vc.Name as category,
                   (SELECT COUNT(*) FROM ViolationType vt WHERE vt.ViolationCategoryId = vc.Id) as type_count
            FROM ViolationCategory vc
            ORDER BY vc.Name
        """,
        parameters={},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_VIOL_003",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "COMMON"],
        question_en="What are the most common violations?",
        question_ar="ما هي المخالفات الأكثر شيوعاً؟",
        variations_en=["Common violations", "Top violations", "Frequent violations"],
        variations_ar=["المخالفات الشائعة", "أكثر المخالفات"],
        keywords_en=["common", "top", "frequent", "violations"],
        keywords_ar=["شائع", "أكثر", "متكرر", "مخالفات"],
        sql="""
            SELECT TOP 10 vt.Name as violation_type, COUNT(*) as count
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
        id="ENT_VIOL_004",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "TOTAL"],
        question_en="How many violations occurred this year?",
        question_ar="كم عدد المخالفات التي حدثت هذا العام؟",
        variations_en=["Total violations", "Violation count", "Number of violations"],
        variations_ar=["إجمالي المخالفات", "عدد المخالفات"],
        keywords_en=["how many", "violations", "total", "count"],
        keywords_ar=["كم", "مخالفات", "إجمالي", "عدد"],
        sql="""
            SELECT COUNT(*) as total_violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.GAUGE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_VIOL_005",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "TREND"],
        question_en="What is the violation trend over time?",
        question_ar="ما هو اتجاه المخالفات مع الوقت؟",
        variations_en=["Violation trend", "Violations over time", "Monthly violations"],
        variations_ar=["اتجاه المخالفات", "المخالفات مع الوقت"],
        keywords_en=["trend", "violations", "over time", "monthly"],
        keywords_ar=["اتجاه", "مخالفات", "مع الوقت", "شهري"],
        sql="""
            SELECT FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
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
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_VIOL_006",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "CATEGORY", "BREAKDOWN"],
        question_en="Show violations by category",
        question_ar="أظهر المخالفات حسب الفئة",
        variations_en=["Violations per category", "Category breakdown", "By category violations"],
        variations_ar=["المخالفات لكل فئة", "تقسيم الفئات"],
        keywords_en=["category", "breakdown", "violations", "by"],
        keywords_ar=["فئة", "تقسيم", "مخالفات", "حسب"],
        sql="""
            SELECT vc.Name as category, COUNT(ev.Id) as count
            FROM ViolationCategory vc
            JOIN ViolationType vt ON vt.ViolationCategoryId = vc.Id
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vc.Id, vc.Name
            ORDER BY count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_VIOL_007",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "SEVERITY"],
        question_en="What is the severity distribution of violations?",
        question_ar="ما هو توزيع شدة المخالفات؟",
        variations_en=["Violation severity", "Severity breakdown", "How severe are violations?"],
        variations_ar=["شدة المخالفات", "توزيع الشدة"],
        keywords_en=["severity", "distribution", "violations", "severe"],
        keywords_ar=["شدة", "توزيع", "مخالفات", "حدة"],
        sql="""
            SELECT 
                CASE 
                    WHEN ev.Value >= 100 THEN 'High'
                    WHEN ev.Value >= 50 THEN 'Medium'
                    ELSE 'Low'
                END as severity,
                COUNT(*) as count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN ev.Value >= 100 THEN 'High' WHEN ev.Value >= 50 THEN 'Medium' ELSE 'Low' END
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.PIE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_VIOL_008",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "DETAILS"],
        question_en="Show details about violation type {violation_type}",
        question_ar="أظهر تفاصيل نوع المخالفة {violation_type}",
        variations_en=["Violation details", "About this violation", "Violation info"],
        variations_ar=["تفاصيل المخالفة", "معلومات المخالفة"],
        keywords_en=["details", "violation", "type", "about"],
        keywords_ar=["تفاصيل", "مخالفة", "نوع", "عن"],
        sql="""
            SELECT vt.Name as violation_type, vc.Name as category,
                   COUNT(ev.Id) as total_occurrences,
                   AVG(ev.Value) as avg_value,
                   COUNT(DISTINCT e.LocationID) as locations_affected
            FROM ViolationType vt
            LEFT JOIN ViolationCategory vc ON vt.ViolationCategoryId = vc.Id
            LEFT JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            LEFT JOIN Event e ON ev.EventId = e.Id AND e.IsDeleted = 0
            WHERE vt.Name LIKE '%{violation_type}%'
            GROUP BY vt.Id, vt.Name, vc.Id, vc.Name
        """,
        parameters={"violation_type": str},
        default_values={},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
    QuestionTemplate(
        id="ENT_VIOL_009",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "RECURRING"],
        question_en="Which violations keep recurring?",
        question_ar="أي المخالفات تتكرر باستمرار؟",
        variations_en=["Recurring violations", "Repeated violations", "Chronic issues"],
        variations_ar=["المخالفات المتكررة", "المخالفات المزمنة"],
        keywords_en=["recurring", "repeated", "chronic", "violations"],
        keywords_ar=["متكرر", "مزمن", "مخالفات"],
        sql="""
            SELECT vt.Name as violation_type,
                   COUNT(*) as total_occurrences,
                   COUNT(DISTINCT e.LocationID) as locations_affected,
                   CAST(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT e.LocationID), 0) AS DECIMAL(5,2)) as avg_per_location
            FROM EventViolation ev
            JOIN ViolationType vt ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name
            HAVING COUNT(*) > 5
            ORDER BY avg_per_location DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_VIOL_010",
        category=QuestionCategory.ENTITY,
        subcategory="violation",
        intent=["VIOLATION", "VALUE"],
        question_en="What is the total value of violations?",
        question_ar="ما هي القيمة الإجمالية للمخالفات؟",
        variations_en=["Violation total value", "Sum of violations", "Violation costs"],
        variations_ar=["إجمالي قيمة المخالفات", "مجموع المخالفات"],
        keywords_en=["value", "total", "sum", "violations"],
        keywords_ar=["قيمة", "إجمالي", "مجموع", "مخالفات"],
        sql="""
            SELECT SUM(ev.Value) as total_value,
                   AVG(ev.Value) as avg_value,
                   MAX(ev.Value) as max_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
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
# REGISTER ALL EXTENDED ENTITY QUESTIONS
# ============================================================================

ALL_EXTENDED_ENTITY_QUESTIONS = (
    INSPECTOR_ENTITY_QUESTIONS +
    LOCATION_ENTITY_QUESTIONS +
    NEIGHBORHOOD_ENTITY_QUESTIONS +
    VIOLATION_ENTITY_QUESTIONS
)

# Register all questions
registry.register_many(ALL_EXTENDED_ENTITY_QUESTIONS)

print(f"Extended Entity Questions loaded: {len(ALL_EXTENDED_ENTITY_QUESTIONS)} templates")
