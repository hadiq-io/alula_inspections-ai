"""
SQL Templates - Violations Domain
=================================
Working templates for violation-related questions.
EventViolation: EventId, ViolationValue, Severity (0 or NULL), HasObjection, ObjectionStatus
"""

TEMPLATES = {
    "violations_total_count": {
        "id": "VIO_01",
        "intents": ["COUNT"],
        "question_ar": "كم عدد المخالفات الإجمالي؟",
        "question_en": "What is the total number of violations?",
        "default_chart": "none",
        "sql": """
            SELECT COUNT(*) as total_violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_by_year": {
        "id": "VIO_02",
        "intents": ["TREND", "COMPARISON"],
        "question_ar": "المخالفات حسب السنة",
        "question_en": "Violations by year",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) as year,
                COUNT(*) as violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        "filters": {}
    },
    
    "violations_monthly_trend": {
        "id": "VIO_03",
        "intents": ["TREND", "COUNT"],
        "question_ar": "اتجاهات المخالفات الشهرية",
        "question_en": "Monthly violation trends",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(*) as violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_with_objections": {
        "id": "VIO_04",
        "intents": ["COUNT", "FILTER"],
        "question_ar": "المخالفات مع اعتراضات",
        "question_en": "Violations with objections",
        "default_chart": "pie",
        "sql": """
            SELECT 
                CASE 
                    WHEN ev.HasObjection = 1 THEN 'Has Objection'
                    ELSE 'No Objection'
                END as status,
                COUNT(*) as count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY ev.HasObjection
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_objection_status": {
        "id": "VIO_05",
        "intents": ["COUNT", "RANKING"],
        "question_ar": "حالة الاعتراضات على المخالفات",
        "question_en": "Violation objection status breakdown",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE ev.ObjectionStatus
                    WHEN 0 THEN 'Pending'
                    WHEN 1 THEN 'Approved'
                    WHEN 2 THEN 'Rejected'
                    ELSE 'Status ' + CAST(COALESCE(ev.ObjectionStatus, 0) AS VARCHAR)
                END as objection_status,
                COUNT(*) as count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND ev.HasObjection = 1
            {year_filter}
            GROUP BY ev.ObjectionStatus
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_by_value": {
        "id": "VIO_06",
        "intents": ["COUNT", "RANKING"],
        "question_ar": "المخالفات حسب القيمة",
        "question_en": "Violations by value/amount",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                CASE 
                    WHEN ev.ViolationValue = 0 THEN '0 (No Fine)'
                    WHEN ev.ViolationValue <= 1000 THEN '1-1000'
                    WHEN ev.ViolationValue <= 5000 THEN '1001-5000'
                    WHEN ev.ViolationValue <= 10000 THEN '5001-10000'
                    ELSE '10000+'
                END as value_range,
                COUNT(*) as count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY CASE 
                WHEN ev.ViolationValue = 0 THEN '0 (No Fine)'
                WHEN ev.ViolationValue <= 1000 THEN '1-1000'
                WHEN ev.ViolationValue <= 5000 THEN '1001-5000'
                WHEN ev.ViolationValue <= 10000 THEN '5001-10000'
                ELSE '10000+'
            END
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_total_value": {
        "id": "VIO_07",
        "intents": ["SUM", "COUNT"],
        "question_ar": "إجمالي قيمة المخالفات",
        "question_en": "Total violation value/fines",
        "default_chart": "none",
        "sql": """
            SELECT 
                COUNT(*) as total_violations,
                SUM(COALESCE(ev.ViolationValue, 0)) as total_fines,
                AVG(CAST(COALESCE(ev.ViolationValue, 0) AS FLOAT)) as avg_fine
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_by_question": {
        "id": "VIO_08",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "أكثر المخالفات شيوعاً",
        "question_en": "Most common violations by type",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(ev.QuestionNameEn, 'Unknown') as violation_type,
                COALESCE(ev.QuestionNameAr, 'غير معروف') as violation_type_ar,
                COUNT(*) as count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY ev.QuestionNameEn, ev.QuestionNameAr
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_by_activity_type": {
        "id": "VIO_13",
        "intents": ["RANKING", "COUNT", "FILTER"],
        "question_ar": "المخالفات الأكثر تكراراً حسب نوع النشاط",
        "question_en": "Most recurring violations by sector/activity type",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(ev.QuestionNameEn, 'Unknown') as violation_type,
                COALESCE(ev.QuestionNameAr, N'غير معروف') as violation_type_ar,
                COUNT(*) as count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            {activity_filter}
            GROUP BY ev.QuestionNameEn, ev.QuestionNameAr
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}",
            "activity_filter": "AND (lt.Name LIKE N'%{activity}%' OR lt.NameAr LIKE N'%{activity}%')"
        }
    },
    
    "violations_repeat_locations": {
        "id": "VIO_09",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المواقع الأكثر مخالفات متكررة",
        "question_en": "Locations with repeat violations",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Unknown') as location_name,
                COUNT(*) as violation_count
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            LEFT JOIN Locations l ON e.Location = l.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY l.Name
            HAVING COUNT(*) > 1
            ORDER BY violation_count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_by_event_type": {
        "id": "VIO_10",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المخالفات حسب نوع الحدث",
        "question_en": "Violations by event type",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(et.NameEn, 'Unknown') as event_type,
                COUNT(*) as violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            LEFT JOIN EventType et ON e.EventType = et.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY et.NameEn
            ORDER BY violations DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_rate": {
        "id": "VIO_11",
        "intents": ["AVERAGE", "COUNT"],
        "question_ar": "معدل المخالفات",
        "question_en": "Violation rate (violations per inspection)",
        "default_chart": "none",
        "sql": """
            SELECT 
                COUNT(DISTINCT e.Id) as total_inspections,
                COUNT(ev.Id) as total_violations,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0), 2) as violations_per_inspection
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "violations_this_year": {
        "id": "VIO_12",
        "intents": ["COUNT", "TREND"],
        "question_ar": "مخالفات هذا العام",
        "question_en": "Violations this year",
        "default_chart": "line",
        "sql": """
            SELECT 
                DATENAME(MONTH, e.SubmitionDate) as month,
                MONTH(e.SubmitionDate) as month_num,
                COUNT(*) as violations
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = 2025
            GROUP BY DATENAME(MONTH, e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY month_num
        """,
        "filters": {}
    }
}
