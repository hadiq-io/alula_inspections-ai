"""
SQL Templates - Locations/Neighborhoods Domain
==============================================
Working templates for location-related questions.
Locations: Id, Name, NameAr, LocationType
Event.Location -> Locations.Id
"""

TEMPLATES = {
    "locations_list": {
        "id": "LOC_00",
        "intents": ["LIST", "DETAIL", "FILTER"],
        "question_ar": "قائمة المواقع",
        "question_en": "List of locations",
        "default_chart": "none",
        "sql": """
            SELECT TOP 50
                l.Name as location_name,
                l.NameAr as location_name_ar,
                COALESCE(lt.Name, 'Unknown') as location_type,
                l.Category as category,
                l.Address as address,
                CASE WHEN l.IsActive = 1 THEN 'Active' ELSE 'Inactive' END as status
            FROM Locations l
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE l.Isdeleted = 0
            ORDER BY l.Name
        """,
        "filters": {}
    },
    
    "locations_total_count": {
        "id": "LOC_01",
        "intents": ["COUNT"],
        "question_ar": "كم عدد المواقع الإجمالي؟",
        "question_en": "How many total locations are there?",
        "default_chart": "none",
        "sql": """
            SELECT COUNT(*) as total_locations
            FROM Locations l
            WHERE l.Isdeleted = 0
        """,
        "filters": {}
    },
    
    "locations_by_type": {
        "id": "LOC_02",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المواقع حسب النوع",
        "question_en": "Locations by type",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 15
                COALESCE(lt.Name, 'Unknown') as location_type,
                COUNT(*) as count
            FROM Locations l
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE l.Isdeleted = 0
            GROUP BY lt.Name
            ORDER BY count DESC
        """,
        "filters": {}
    },
    
    "locations_most_inspected": {
        "id": "LOC_03",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المواقع الأكثر تفتيشاً",
        "question_en": "Most inspected locations",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Unknown') as location,
                COUNT(*) as inspections
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            WHERE e.IsDeleted = 0 AND l.Id IS NOT NULL
            {year_filter}
            GROUP BY l.Name
            ORDER BY inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_by_violations": {
        "id": "LOC_04",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المواقع حسب عدد المخالفات",
        "question_en": "Locations by violation count",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Unknown') as location,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND l.Id IS NOT NULL
            {year_filter}
            GROUP BY l.Name
            ORDER BY violations DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_compliance_score": {
        "id": "LOC_05",
        "intents": ["RANKING", "AVERAGE"],
        "question_ar": "درجة الامتثال حسب الموقع",
        "question_en": "Compliance score by location",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Unknown') as location,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                COUNT(*) as inspections
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            WHERE e.IsDeleted = 0 AND l.Id IS NOT NULL AND e.Score IS NOT NULL
            {year_filter}
            GROUP BY l.Name
            HAVING COUNT(*) >= 5
            ORDER BY avg_score DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_lowest_compliance": {
        "id": "LOC_06",
        "intents": ["RANKING", "AVERAGE"],
        "question_ar": "المواقع الأقل امتثالاً",
        "question_en": "Locations with lowest compliance",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Unknown') as location,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                COUNT(*) as inspections,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            WHERE e.IsDeleted = 0 AND l.Id IS NOT NULL AND e.Score IS NOT NULL
            {year_filter}
            GROUP BY l.Name
            HAVING COUNT(*) >= 5
            ORDER BY avg_score ASC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_high_risk": {
        "id": "LOC_07",
        "intents": ["RANKING", "FILTER", "RISK", "HIGH_RISK"],
        "question_ar": "المواقع عالية المخاطر",
        "question_en": "High-risk locations",
        "keywords_en": ["high risk", "high-risk", "risky locations", "dangerous", "which locations are high risk"],
        "keywords_ar": ["مخاطر عالية", "مواقع خطرة"],
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Location ID: ' + CAST(e.Location AS VARCHAR)) as location,
                COUNT(ev.Id) as violations,
                SUM(COALESCE(e.CriticalIssueCount, 0)) as critical_issues,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY e.Location, l.Name
            HAVING COUNT(ev.Id) > 0 OR SUM(COALESCE(e.CriticalIssueCount, 0)) > 0
            ORDER BY violations DESC, critical_issues DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_inspection_frequency": {
        "id": "LOC_08",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "تكرار التفتيش حسب الموقع",
        "question_en": "Inspection frequency by location",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE 
                    WHEN cnt = 1 THEN '1 inspection'
                    WHEN cnt <= 5 THEN '2-5 inspections'
                    WHEN cnt <= 10 THEN '6-10 inspections'
                    WHEN cnt <= 50 THEN '11-50 inspections'
                    ELSE '50+ inspections'
                END as frequency,
                COUNT(*) as location_count
            FROM (
                SELECT e.Location, COUNT(*) as cnt
                FROM Event e
                WHERE e.IsDeleted = 0 AND e.Location IS NOT NULL
                {year_filter}
                GROUP BY e.Location
            ) sub
            GROUP BY CASE 
                WHEN cnt = 1 THEN '1 inspection'
                WHEN cnt <= 5 THEN '2-5 inspections'
                WHEN cnt <= 10 THEN '6-10 inspections'
                WHEN cnt <= 50 THEN '11-50 inspections'
                ELSE '50+ inspections'
            END
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_by_category": {
        "id": "LOC_09",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المواقع حسب الفئة",
        "question_en": "Locations by category",
        "default_chart": "pie",
        "sql": """
            SELECT TOP 10
                CASE l.Category
                    WHEN 1 THEN 'Category 1'
                    WHEN 2 THEN 'Category 2'
                    WHEN 3 THEN 'Category 3'
                    ELSE 'Other'
                END as category,
                COUNT(*) as count
            FROM Locations l
            WHERE l.Isdeleted = 0
            GROUP BY l.Category
            ORDER BY count DESC
        """,
        "filters": {}
    },
    
    "locations_monthly_inspections": {
        "id": "LOC_10",
        "intents": ["TREND", "COUNT"],
        "question_ar": "التفتيشات الشهرية حسب نوع الموقع",
        "question_en": "Monthly inspections by location type",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(*) as inspections
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_comparison": {
        "id": "LOC_11",
        "intents": ["COMPARISON", "RANKING"],
        "question_ar": "مقارنة بين أنواع المواقع",
        "question_en": "Location type comparison",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(lt.Name, 'Unknown') as location_type,
                COUNT(*) as inspections,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY lt.Name
            ORDER BY inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "locations_without_inspections": {
        "id": "LOC_12",
        "intents": ["COUNT", "FILTER"],
        "question_ar": "المواقع التي لم يتم تفتيشها",
        "question_en": "Locations without inspections",
        "default_chart": "none",
        "sql": """
            SELECT 
                COUNT(*) as locations_not_inspected
            FROM Locations l
            WHERE l.Isdeleted = 0
              AND l.Id NOT IN (
                  SELECT DISTINCT e.Location 
                  FROM Event e 
                  WHERE e.IsDeleted = 0 AND e.Location IS NOT NULL
                  {year_filter}
              )
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    }
}
