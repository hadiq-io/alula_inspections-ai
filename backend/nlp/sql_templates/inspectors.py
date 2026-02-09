"""
SQL Templates - Inspectors Domain
=================================
Working templates for inspector-related questions.
Event.ReporterID is the inspector ID
"""

TEMPLATES = {
    "inspectors_total_count": {
        "id": "INS_01",
        "intents": ["COUNT"],
        "question_ar": "كم عدد المفتشين النشطين؟",
        "question_en": "How many active inspectors are there?",
        "default_chart": "none",
        "sql": """
            SELECT COUNT(DISTINCT e.ReporterID) as active_inspectors
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_top_performers": {
        "id": "INS_02",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "أفضل المفتشين أداءً",
        "question_en": "Top performing inspectors",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                COUNT(*) as inspections,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            {year_filter}
            GROUP BY e.ReporterID
            ORDER BY inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_by_inspection_count": {
        "id": "INS_03",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المفتشين حسب عدد التفتيشات",
        "question_en": "Inspectors by inspection count",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 15
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                COUNT(*) as total_inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            {year_filter}
            GROUP BY e.ReporterID
            ORDER BY total_inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_avg_score": {
        "id": "INS_04",
        "intents": ["AVERAGE", "RANKING"],
        "question_ar": "متوسط درجة المفتشين",
        "question_en": "Inspector average scores",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                COUNT(*) as inspections,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL AND e.Score IS NOT NULL
            {year_filter}
            GROUP BY e.ReporterID
            HAVING COUNT(*) >= 10
            ORDER BY avg_score DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_workload_distribution": {
        "id": "INS_05",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "توزيع عبء العمل بين المفتشين",
        "question_en": "Inspector workload distribution",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE 
                    WHEN cnt <= 100 THEN '1-100 inspections'
                    WHEN cnt <= 500 THEN '101-500 inspections'
                    WHEN cnt <= 1000 THEN '501-1000 inspections'
                    WHEN cnt <= 5000 THEN '1001-5000 inspections'
                    ELSE '5000+ inspections'
                END as workload_tier,
                COUNT(*) as inspector_count
            FROM (
                SELECT e.ReporterID, COUNT(*) as cnt
                FROM Event e
                WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
                {year_filter}
                GROUP BY e.ReporterID
            ) sub
            GROUP BY CASE 
                WHEN cnt <= 100 THEN '1-100 inspections'
                WHEN cnt <= 500 THEN '101-500 inspections'
                WHEN cnt <= 1000 THEN '501-1000 inspections'
                WHEN cnt <= 5000 THEN '1001-5000 inspections'
                ELSE '5000+ inspections'
            END
            ORDER BY inspector_count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_issues_found": {
        "id": "INS_06",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المفتشين الذين وجدوا أكثر المشاكل",
        "question_en": "Inspectors who found most issues",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            {year_filter}
            GROUP BY e.ReporterID
            ORDER BY total_issues DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_critical_issues": {
        "id": "INS_07",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المفتشين الذين وجدوا مشاكل حرجة",
        "question_en": "Inspectors who found critical issues",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                SUM(COALESCE(e.CriticalIssueCount, 0)) as critical_issues,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL AND e.CriticalIssueCount > 0
            {year_filter}
            GROUP BY e.ReporterID
            ORDER BY critical_issues DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_monthly_activity": {
        "id": "INS_08",
        "intents": ["TREND", "COUNT"],
        "question_ar": "نشاط المفتشين الشهري",
        "question_en": "Monthly inspector activity",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(DISTINCT e.ReporterID) as active_inspectors,
                COUNT(*) as total_inspections
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
    
    "inspectors_avg_duration": {
        "id": "INS_09",
        "intents": ["AVERAGE", "RANKING"],
        "question_ar": "متوسط مدة التفتيش لكل مفتش",
        "question_en": "Average inspection duration by inspector",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                ROUND(AVG(CAST(e.Duration AS FLOAT)) / 60, 2) as avg_minutes,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL AND e.Duration > 0
            {year_filter}
            GROUP BY e.ReporterID
            HAVING COUNT(*) >= 10
            ORDER BY avg_minutes
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_violations_found": {
        "id": "INS_10",
        "intents": ["RANKING", "COUNT"],
        "question_ar": "المخالفات المكتشفة لكل مفتش",
        "question_en": "Violations found by inspector",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                'Inspector ' + CAST(e.ReporterID AS VARCHAR) as inspector,
                COUNT(ev.Id) as violations_found,
                COUNT(DISTINCT e.Id) as inspections
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            {year_filter}
            GROUP BY e.ReporterID
            ORDER BY violations_found DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_performance_stats": {
        "id": "INS_11",
        "intents": ["DETAIL", "COUNT"],
        "question_ar": "إحصائيات أداء المفتشين",
        "question_en": "Inspector performance statistics",
        "default_chart": "none",
        "sql": """
            SELECT 
                COUNT(DISTINCT e.ReporterID) as total_inspectors,
                COUNT(*) as total_inspections,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as overall_avg_score,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues_found,
                ROUND(AVG(CAST(e.Duration AS FLOAT)) / 60, 2) as avg_duration_minutes
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "inspectors_yearly_comparison": {
        "id": "INS_12",
        "intents": ["TREND", "COMPARISON"],
        "question_ar": "مقارنة عدد المفتشين سنوياً",
        "question_en": "Yearly inspector count comparison",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) as year,
                COUNT(DISTINCT e.ReporterID) as active_inspectors,
                COUNT(*) as total_inspections
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY year
        """,
        "filters": {}
    }
}
