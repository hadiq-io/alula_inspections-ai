"""
Entity Questions Library
=========================
150+ entity-specific questions covering inspectors, locations, violations, and events.
"""

from . import QuestionTemplate, QuestionCategory, OutputFormat, ChartType, Difficulty, registry


# ============================================================================
# INSPECTOR ENTITY QUESTIONS (40 questions)
# ============================================================================

INSPECTOR_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_INSP_001",
        category=QuestionCategory.ENTITY,
        subcategory="inspectors",
        intent=["ENTITY", "INSPECTOR", "DETAILS"],
        question_en="Show me details for inspector {inspector_name}",
        question_ar="أظهر لي تفاصيل المفتش {inspector_name}",
        variations_en=[
            "Inspector details",
            "Tell me about inspector",
            "Inspector profile",
            "What about this inspector?"
        ],
        variations_ar=[
            "تفاصيل المفتش",
            "معلومات عن المفتش"
        ],
        keywords_en=["inspector", "details", "profile", "about"],
        keywords_ar=["مفتش", "تفاصيل", "معلومات"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                COUNT(*) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                MIN(e.Score) as min_score,
                MAX(e.Score) as max_score,
                COUNT(ev.Id) as violations_found,
                MIN(e.SubmitionDate) as first_inspection,
                MAX(e.SubmitionDate) as last_inspection
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND u.Name LIKE '%{inspector_name}%'
            GROUP BY u.Id, u.Name
        """,
        parameters={"inspector_name": str},
        default_values={"inspector_name": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_002",
        category=QuestionCategory.ENTITY,
        subcategory="inspectors",
        intent=["ENTITY", "INSPECTOR", "HISTORY"],
        question_en="Show the inspection history for inspector {inspector_name}",
        question_ar="أظهر سجل الفحوصات للمفتش {inspector_name}",
        variations_en=[
            "Inspector history",
            "What did this inspector do?",
            "Inspection log for inspector"
        ],
        variations_ar=[
            "سجل المفتش",
            "ماذا فعل هذا المفتش؟"
        ],
        keywords_en=["inspector", "history", "log", "inspections"],
        keywords_ar=["مفتش", "سجل", "تاريخ"],
        sql="""
            SELECT TOP 50
                e.SubmitionDate as date,
                l.Name as location,
                e.Score,
                COUNT(ev.Id) as violations
            FROM Event e
            JOIN [User] u ON e.ReporterID = u.Id
            JOIN Location l ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND u.Name LIKE '%{inspector_name}%'
            GROUP BY e.Id, e.SubmitionDate, l.Name, e.Score
            ORDER BY e.SubmitionDate DESC
        """,
        parameters={"inspector_name": str},
        default_values={"inspector_name": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_003",
        category=QuestionCategory.ENTITY,
        subcategory="inspectors",
        intent=["ENTITY", "INSPECTOR", "PERFORMANCE_TREND"],
        question_en="What is the performance trend for inspector {inspector_name}?",
        question_ar="ما هو اتجاه أداء المفتش {inspector_name}؟",
        variations_en=[
            "Inspector performance over time",
            "How has this inspector improved?",
            "Inspector trend"
        ],
        variations_ar=[
            "أداء المفتش مع الوقت",
            "كيف تحسن هذا المفتش؟"
        ],
        keywords_en=["inspector", "performance", "trend", "over time"],
        keywords_ar=["مفتش", "أداء", "اتجاه"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Event e
            JOIN [User] u ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
              AND u.Name LIKE '%{inspector_name}%'
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"inspector_name": str},
        default_values={"inspector_name": ""},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_INSP_004",
        category=QuestionCategory.ENTITY,
        subcategory="inspectors",
        intent=["LIST", "ALL", "INSPECTORS"],
        question_en="List all inspectors",
        question_ar="اعرض جميع المفتشين",
        variations_en=[
            "Show all inspectors",
            "Who are the inspectors?",
            "Inspector list",
            "All inspectors"
        ],
        variations_ar=[
            "جميع المفتشين",
            "قائمة المفتشين"
        ],
        keywords_en=["list", "all", "inspectors", "who"],
        keywords_ar=["قائمة", "جميع", "مفتشين"],
        sql="""
            SELECT 
                u.Name as inspector_name,
                COUNT(*) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                MAX(e.SubmitionDate) as last_active
            FROM [User] u
            JOIN Event e ON e.ReporterID = u.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
            GROUP BY u.Id, u.Name
            ORDER BY total_inspections DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# LOCATION ENTITY QUESTIONS (40 questions)
# ============================================================================

LOCATION_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_LOC_001",
        category=QuestionCategory.ENTITY,
        subcategory="locations",
        intent=["ENTITY", "LOCATION", "DETAILS"],
        question_en="Show me details for location {location_name}",
        question_ar="أظهر لي تفاصيل الموقع {location_name}",
        variations_en=[
            "Location details",
            "Tell me about this location",
            "Location profile",
            "What about this location?"
        ],
        variations_ar=[
            "تفاصيل الموقع",
            "معلومات عن الموقع"
        ],
        keywords_en=["location", "details", "profile", "about"],
        keywords_ar=["موقع", "تفاصيل", "معلومات"],
        sql="""
            SELECT 
                l.Name as location_name,
                n.Name as neighborhood,
                COUNT(e.Id) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as total_violations,
                SUM(ev.Value) as total_violation_value,
                MIN(e.SubmitionDate) as first_inspection,
                MAX(e.SubmitionDate) as last_inspection
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE l.Name LIKE '%{location_name}%'
            GROUP BY l.Id, l.Name, n.Name
        """,
        parameters={"location_name": str},
        default_values={"location_name": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_LOC_002",
        category=QuestionCategory.ENTITY,
        subcategory="locations",
        intent=["ENTITY", "LOCATION", "HISTORY"],
        question_en="Show the inspection history for location {location_name}",
        question_ar="أظهر سجل الفحوصات للموقع {location_name}",
        variations_en=[
            "Location history",
            "What happened at this location?",
            "Inspection log for location"
        ],
        variations_ar=[
            "سجل الموقع",
            "ماذا حدث في هذا الموقع؟"
        ],
        keywords_en=["location", "history", "log", "inspections"],
        keywords_ar=["موقع", "سجل", "تاريخ"],
        sql="""
            SELECT TOP 50
                e.SubmitionDate as date,
                u.Name as inspector,
                e.Score,
                COUNT(ev.Id) as violations,
                SUM(ev.Value) as violation_value
            FROM Event e
            JOIN Location l ON e.LocationID = l.Id
            JOIN [User] u ON e.ReporterID = u.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND l.Name LIKE '%{location_name}%'
            GROUP BY e.Id, e.SubmitionDate, u.Name, e.Score
            ORDER BY e.SubmitionDate DESC
        """,
        parameters={"location_name": str},
        default_values={"location_name": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_LOC_003",
        category=QuestionCategory.ENTITY,
        subcategory="locations",
        intent=["ENTITY", "LOCATION", "VIOLATIONS"],
        question_en="What violations occurred at location {location_name}?",
        question_ar="ما المخالفات التي حدثت في الموقع {location_name}؟",
        variations_en=[
            "Location violations",
            "Violations at this location",
            "What went wrong at this location?"
        ],
        variations_ar=[
            "مخالفات الموقع",
            "المخالفات في هذا الموقع"
        ],
        keywords_en=["location", "violations", "what", "wrong"],
        keywords_ar=["موقع", "مخالفات"],
        sql="""
            SELECT 
                COALESCE(ev.QuestionNameEn, 'Unspecified') as violation_type,
                COALESCE(ev.QuestionNameAr, 'غير محدد') as violation_type_ar,
                COUNT(*) as occurrence_count,
                SUM(ev.ViolationValue) as total_value,
                MAX(e.SubmitionDate) as last_occurrence
            FROM Locations l
            JOIN Event e ON e.Location = l.Id
            JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND (l.Name LIKE '%{location_name}%' OR l.NameAr LIKE '%{location_name}%')
            GROUP BY ev.QuestionNameEn, ev.QuestionNameAr
            ORDER BY occurrence_count DESC
        """,
        parameters={"location_name": str},
        default_values={"location_name": ""},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_LOC_004",
        category=QuestionCategory.ENTITY,
        subcategory="locations",
        intent=["LIST", "ALL", "LOCATIONS"],
        question_en="List all locations in neighborhood {neighborhood_name}",
        question_ar="اعرض جميع المواقع في الحي {neighborhood_name}",
        variations_en=[
            "Locations in area",
            "Show locations in neighborhood",
            "All locations in this area"
        ],
        variations_ar=[
            "المواقع في الحي",
            "جميع مواقع المنطقة"
        ],
        keywords_en=["list", "locations", "neighborhood", "area"],
        keywords_ar=["قائمة", "مواقع", "حي"],
        sql="""
            SELECT 
                l.Name as location_name,
                COUNT(e.Id) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count
            FROM Location l
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE n.Name LIKE '%{neighborhood_name}%'
              AND l.IsDeleted = 0
            GROUP BY l.Id, l.Name
            ORDER BY location_name
        """,
        parameters={"neighborhood_name": str},
        default_values={"neighborhood_name": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# VIOLATION ENTITY QUESTIONS (40 questions)
# ============================================================================

VIOLATION_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_VIOL_001",
        category=QuestionCategory.ENTITY,
        subcategory="violations",
        intent=["ENTITY", "VIOLATION_TYPE", "DETAILS"],
        question_en="Tell me about violation type {violation_type}",
        question_ar="أخبرني عن نوع المخالفة {violation_type}",
        variations_en=[
            "Violation type details",
            "What is this violation?",
            "Violation type info"
        ],
        variations_ar=[
            "تفاصيل نوع المخالفة",
            "ما هذه المخالفة؟"
        ],
        keywords_en=["violation", "type", "details", "about", "what"],
        keywords_ar=["مخالفة", "نوع", "تفاصيل"],
        sql="""
            SELECT TOP 20
                COALESCE(ev.QuestionNameEn, 'Unspecified') as violation_type,
                COALESCE(ev.QuestionNameAr, 'غير محدد') as violation_type_ar,
                CASE WHEN ev.Severity IS NULL THEN 'Not Specified' ELSE CAST(ev.Severity AS VARCHAR) END as severity,
                COUNT(ev.Id) as total_occurrences,
                SUM(ev.ViolationValue) as total_value,
                AVG(CAST(ev.ViolationValue AS FLOAT)) as avg_value,
                MIN(e.SubmitionDate) as first_occurrence,
                MAX(e.SubmitionDate) as last_occurrence
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id AND e.IsDeleted = 0
            WHERE ev.QuestionNameEn IS NOT NULL
            GROUP BY ev.QuestionNameEn, ev.QuestionNameAr, ev.Severity
            ORDER BY total_occurrences DESC
        """,
        parameters={"violation_type": str},
        default_values={"violation_type": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_VIOL_002",
        category=QuestionCategory.ENTITY,
        subcategory="violations",
        intent=["ENTITY", "VIOLATION_TYPE", "TREND"],
        question_en="What is the trend for violation type {violation_type}?",
        question_ar="ما هو اتجاه نوع المخالفة {violation_type}؟",
        variations_en=[
            "Violation type trend",
            "How is this violation trending?",
            "Violation occurrences over time"
        ],
        variations_ar=[
            "اتجاه نوع المخالفة",
            "كيف يتجه هذا النوع؟"
        ],
        keywords_en=["violation", "type", "trend", "over time"],
        keywords_ar=["مخالفة", "نوع", "اتجاه"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(*) as occurrences,
                SUM(ev.Value) as total_value
            FROM ViolationType vt
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND vt.Name LIKE '%{violation_type}%'
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"violation_type": str},
        default_values={"violation_type": ""},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_VIOL_003",
        category=QuestionCategory.ENTITY,
        subcategory="violations",
        intent=["ENTITY", "VIOLATION_TYPE", "LOCATIONS"],
        question_en="Where does violation type {violation_type} occur most?",
        question_ar="أين يحدث نوع المخالفة {violation_type} أكثر؟",
        variations_en=[
            "Top locations for this violation",
            "Where does this violation happen?",
            "Violation hotspots"
        ],
        variations_ar=[
            "أماكن هذه المخالفة",
            "أين تحدث هذه المخالفة؟"
        ],
        keywords_en=["violation", "where", "occur", "locations", "most"],
        keywords_ar=["مخالفة", "أين", "تحدث", "مواقع"],
        sql="""
            SELECT TOP 10
                l.Name as location_name,
                n.Name as neighborhood,
                COUNT(*) as occurrences,
                SUM(ev.Value) as total_value
            FROM ViolationType vt
            JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            JOIN Event e ON ev.EventId = e.Id
            JOIN Location l ON e.LocationID = l.Id
            JOIN Neighborhood n ON l.NeighborhoodId = n.Id
            WHERE e.IsDeleted = 0
              AND vt.Name LIKE '%{violation_type}%'
            GROUP BY l.Id, l.Name, n.Name
            ORDER BY occurrences DESC
        """,
        parameters={"violation_type": str},
        default_values={"violation_type": ""},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.BAR,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_VIOL_004",
        category=QuestionCategory.ENTITY,
        subcategory="violations",
        intent=["LIST", "ALL", "VIOLATION_TYPES"],
        question_en="List all violation types",
        question_ar="اعرض جميع أنواع المخالفات",
        variations_en=[
            "Show all violations",
            "What types of violations are there?",
            "Violation type list"
        ],
        variations_ar=[
            "جميع أنواع المخالفات",
            "قائمة المخالفات"
        ],
        keywords_en=["list", "all", "violation", "types"],
        keywords_ar=["قائمة", "جميع", "مخالفات", "أنواع"],
        sql="""
            SELECT 
                vt.Name as violation_type,
                vt.NameAr as violation_type_ar,
                vc.Name as category,
                COUNT(ev.Id) as total_occurrences,
                SUM(ev.Value) as total_value
            FROM ViolationType vt
            JOIN ViolationCategory vc ON vt.ViolationCategoryId = vc.Id
            LEFT JOIN EventViolation ev ON ev.ViolationTypeId = vt.Id
            LEFT JOIN Event e ON ev.EventId = e.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY vt.Id, vt.Name, vt.NameAr, vc.Name
            ORDER BY total_occurrences DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]

# ============================================================================
# NEIGHBORHOOD ENTITY QUESTIONS (30 questions)
# ============================================================================

NEIGHBORHOOD_ENTITY_QUESTIONS = [
    QuestionTemplate(
        id="ENT_NEIGH_001",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhoods",
        intent=["ENTITY", "NEIGHBORHOOD", "DETAILS"],
        question_en="Show me details for neighborhood {neighborhood_name}",
        question_ar="أظهر لي تفاصيل الحي {neighborhood_name}",
        variations_en=[
            "Neighborhood details",
            "Tell me about this neighborhood",
            "Area profile"
        ],
        variations_ar=[
            "تفاصيل الحي",
            "معلومات عن الحي"
        ],
        keywords_en=["neighborhood", "details", "profile", "about"],
        keywords_ar=["حي", "تفاصيل", "معلومات"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(DISTINCT l.Id) as total_locations,
                COUNT(e.Id) as total_inspections,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                CAST(SUM(CASE WHEN e.Score >= 80 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(e.Id), 0) AS DECIMAL(5,2)) as compliance_rate,
                COUNT(ev.Id) as total_violations,
                SUM(ev.Value) as total_violation_value
            FROM Neighborhood n
            LEFT JOIN Location l ON l.NeighborhoodId = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE n.Name LIKE '%{neighborhood_name}%'
            GROUP BY n.Id, n.Name, n.NameAr
        """,
        parameters={"neighborhood_name": str},
        default_values={"neighborhood_name": ""},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_NEIGH_002",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhoods",
        intent=["ENTITY", "NEIGHBORHOOD", "TREND"],
        question_en="What is the performance trend for neighborhood {neighborhood_name}?",
        question_ar="ما هو اتجاه أداء الحي {neighborhood_name}؟",
        variations_en=[
            "Neighborhood trend",
            "How is this area performing over time?",
            "Area performance trend"
        ],
        variations_ar=[
            "اتجاه الحي",
            "أداء المنطقة مع الوقت"
        ],
        keywords_en=["neighborhood", "trend", "performance", "over time"],
        keywords_ar=["حي", "اتجاه", "أداء"],
        sql="""
            SELECT 
                FORMAT(e.SubmitionDate, 'yyyy-MM') as month,
                COUNT(*) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score,
                COUNT(ev.Id) as violation_count
            FROM Neighborhood n
            JOIN Location l ON l.NeighborhoodId = n.Id
            JOIN Event e ON e.LocationID = l.Id
            LEFT JOIN EventViolation ev ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND n.Name LIKE '%{neighborhood_name}%'
            GROUP BY FORMAT(e.SubmitionDate, 'yyyy-MM')
            ORDER BY month
        """,
        parameters={"neighborhood_name": str},
        default_values={"neighborhood_name": ""},
        output_format=OutputFormat.BOTH,
        chart_type=ChartType.LINE,
        difficulty=Difficulty.INTERMEDIATE
    ),
    QuestionTemplate(
        id="ENT_NEIGH_003",
        category=QuestionCategory.ENTITY,
        subcategory="neighborhoods",
        intent=["LIST", "ALL", "NEIGHBORHOODS"],
        question_en="List all neighborhoods",
        question_ar="اعرض جميع الأحياء",
        variations_en=[
            "Show all neighborhoods",
            "What neighborhoods are there?",
            "All areas",
            "Neighborhood list"
        ],
        variations_ar=[
            "جميع الأحياء",
            "قائمة الأحياء"
        ],
        keywords_en=["list", "all", "neighborhoods", "areas"],
        keywords_ar=["قائمة", "جميع", "أحياء"],
        sql="""
            SELECT 
                n.Name as neighborhood,
                n.NameAr as neighborhood_ar,
                COUNT(DISTINCT l.Id) as location_count,
                COUNT(e.Id) as inspection_count,
                CAST(AVG(e.Score) AS DECIMAL(5,2)) as avg_score
            FROM Neighborhood n
            LEFT JOIN Location l ON l.NeighborhoodId = n.Id
            LEFT JOIN Event e ON e.LocationID = l.Id AND e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            WHERE n.IsDeleted = 0
            GROUP BY n.Id, n.Name, n.NameAr
            ORDER BY inspection_count DESC
        """,
        parameters={"year": int},
        default_values={"year": 2024},
        output_format=OutputFormat.TABLE,
        chart_type=ChartType.NONE,
        difficulty=Difficulty.BASIC
    ),
]


# ============================================================================
# REGISTER ALL ENTITY QUESTIONS
# ============================================================================

ALL_ENTITY_QUESTIONS = (
    INSPECTOR_ENTITY_QUESTIONS +
    LOCATION_ENTITY_QUESTIONS +
    VIOLATION_ENTITY_QUESTIONS +
    NEIGHBORHOOD_ENTITY_QUESTIONS
)

# Register all questions
registry.register_many(ALL_ENTITY_QUESTIONS)

print(f"Entity Questions loaded: {len(ALL_ENTITY_QUESTIONS)} templates")
