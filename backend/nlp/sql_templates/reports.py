"""
SQL Templates - Reports/Inspections Domain
==========================================
Working templates based on actual database schema.
Data exists for years: 2022, 2023, 2024, 2025
Total Events: ~243,000 | Total Violations: ~36,000 | Locations: ~8,000
"""

TEMPLATES = {
    "reports_total_count": {
        "id": "RPT_01",
        "intents": ["COUNT"],
        "question_ar": "كم عدد التفتيشات الإجمالي؟",
        "question_en": "What is the total number of inspections?",
        "default_chart": "none",
        "sql": """
            SELECT COUNT(*) as total_inspections
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_by_status": {
        "id": "RPT_02",
        "intents": ["COUNT", "FILTER", "RANKING"],
        "question_ar": "توزيع التفتيشات حسب الحالة",
        "question_en": "Inspections distribution by status",
        "default_chart": "pie",
        "sql": """
            SELECT TOP 10
                CASE 
                    WHEN e.Status = 1 THEN 'Completed'
                    WHEN e.Status = 2 THEN 'In Progress'
                    WHEN e.Status = 3 THEN 'Pending Review'
                    WHEN e.Status = 5 THEN 'Approved'
                    WHEN e.Status = 27 THEN 'Archived'
                    ELSE 'Status ' + CAST(e.Status AS VARCHAR)
                END as status,
                COUNT(*) as count
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY e.Status
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_by_event_type": {
        "id": "RPT_03",
        "intents": ["COUNT", "RANKING"],
        "question_ar": "التفتيشات حسب نوع الحدث",
        "question_en": "Inspections by event type",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(et.NameEn, 'Unknown') as event_type,
                COUNT(*) as count
            FROM Event e
            LEFT JOIN EventType et ON e.EventType = et.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY et.NameEn
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_monthly_trend": {
        "id": "RPT_04",
        "intents": ["TREND", "COUNT"],
        "question_ar": "اتجاهات التفتيشات الشهرية",
        "question_en": "Monthly inspection trends",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_yearly_comparison": {
        "id": "RPT_05",
        "intents": ["TREND", "COMPARISON"],
        "question_ar": "مقارنة التفتيشات السنوية",
        "question_en": "Yearly inspections comparison",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) as year,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        "filters": {}
    },
    
    "reports_by_location_type": {
        "id": "RPT_06",
        "intents": ["COUNT", "RANKING"],
        "question_ar": "التفتيشات حسب نوع الموقع",
        "question_en": "Inspections by location type",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(lt.Name, 'Unknown') as location_type,
                COUNT(*) as count
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY lt.Name
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_avg_score": {
        "id": "RPT_07",
        "intents": ["AVERAGE", "COUNT"],
        "question_ar": "متوسط درجة التفتيشات",
        "question_en": "Average inspection score",
        "default_chart": "none",
        "sql": """
            SELECT 
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                COUNT(*) as total_inspections,
                ROUND(MIN(e.Score), 2) as min_score,
                ROUND(MAX(e.Score), 2) as max_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_with_issues": {
        "id": "RPT_08",
        "intents": ["COUNT", "FILTER"],
        "question_ar": "التفتيشات التي تحتوي على مشاكل",
        "question_en": "Inspections with issues",
        "default_chart": "pie",
        "sql": """
            SELECT 
                CASE 
                    WHEN e.IssueCount > 0 THEN 'Has Issues'
                    ELSE 'No Issues'
                END as status,
                COUNT(*) as count
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY CASE WHEN e.IssueCount > 0 THEN 'Has Issues' ELSE 'No Issues' END
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_critical_issues": {
        "id": "RPT_09",
        "intents": ["COUNT", "RANKING"],
        "question_ar": "التفتيشات ذات المشاكل الحرجة",
        "question_en": "Inspections with critical issues",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                e.CriticalIssueCount as critical_count,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.CriticalIssueCount > 0
            {year_filter}
            GROUP BY e.CriticalIssueCount
            ORDER BY critical_count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "reports_this_month": {
        "id": "RPT_10",
        "intents": ["COUNT", "TREND"],
        "question_ar": "تفتيشات هذا الشهر",
        "question_en": "This month's inspections",
        "default_chart": "none",
        "sql": """
            SELECT 
                COUNT(*) as inspections_this_month,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues,
                SUM(COALESCE(e.CriticalIssueCount, 0)) as critical_issues,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = 2025
              AND MONTH(e.SubmitionDate) = 12
        """,
        "filters": {}
    },
    
    "reports_daily_activity": {
        "id": "RPT_11",
        "intents": ["TREND", "COUNT"],
        "question_ar": "النشاط اليومي للتفتيشات",
        "question_en": "Daily inspection activity",
        "default_chart": "line",
        "sql": """
            SELECT TOP 30
                CONVERT(VARCHAR(10), e.SubmitionDate, 120) as date,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY CONVERT(VARCHAR(10), e.SubmitionDate, 120)
            ORDER BY date DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    }
}
