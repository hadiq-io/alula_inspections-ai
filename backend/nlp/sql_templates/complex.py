"""
SQL Templates - Complex Queries Domain
========================================
Multi-join queries and complex analytics.
"""

TEMPLATES = {
    "complex_comprehensive_overview": {
        "id": "CMP_01",
        "intents": ["OVERVIEW", "SUMMARY"],
        "question_ar": "نظرة عامة شاملة",
        "question_en": "Comprehensive inspection overview",
        "default_chart": "none",
        "sql": """
            SELECT 
                COUNT(*) as total_inspections,
                SUM(CASE WHEN e.Status = 1 THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN e.Status = 2 THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN e.Status = 5 THEN 1 ELSE 0 END) as approved,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues,
                SUM(COALESCE(e.CriticalIssueCount, 0)) as critical_issues,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                ROUND(AVG(CAST(e.Duration AS FLOAT)), 2) as avg_duration
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_location_performance": {
        "id": "CMP_02",
        "intents": ["RANKING", "PERFORMANCE"],
        "question_ar": "أداء المواقع المتكامل",
        "question_en": "Location performance analysis",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(l.Name, 'Unknown') as location,
                COUNT(e.Id) as inspections,
                COUNT(ev.Id) as violations,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                SUM(COALESCE(e.IssueCount, 0)) as issues,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(e.Id), 0), 2) as violation_rate
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND l.Id IS NOT NULL
            {year_filter}
            GROUP BY l.Name
            ORDER BY inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_inspector_location_matrix": {
        "id": "CMP_03",
        "intents": ["MATRIX", "COMPARISON"],
        "question_ar": "مصفوفة المفتش والموقع",
        "question_en": "Inspector-location coverage matrix",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 20
                e.ReporterID as inspector_id,
                COUNT(DISTINCT e.Location) as unique_locations,
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
    
    "complex_violation_location_analysis": {
        "id": "CMP_04",
        "intents": ["ANALYSIS", "RANKING"],
        "question_ar": "تحليل المخالفات والمواقع",
        "question_en": "Violation by location type analysis",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(lt.Name, 'Unknown') as location_type,
                COUNT(DISTINCT e.Id) as inspections,
                COUNT(ev.Id) as violations,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0), 2) as violations_per_inspection,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY lt.Name
            ORDER BY violations DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_monthly_summary": {
        "id": "CMP_05",
        "intents": ["SUMMARY", "TREND"],
        "question_ar": "ملخص شهري",
        "question_en": "Monthly performance summary",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(DISTINCT e.Id) as inspections,
                COUNT(ev.Id) as violations,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                SUM(COALESCE(e.IssueCount, 0)) as issues
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_status_workflow": {
        "id": "CMP_06",
        "intents": ["WORKFLOW", "STATUS"],
        "question_ar": "سير عمل الحالات",
        "question_en": "Status workflow analysis",
        "default_chart": "pie",
        "sql": """
            SELECT 
                CASE e.Status
                    WHEN 1 THEN 'Completed'
                    WHEN 2 THEN 'In Progress'
                    WHEN 3 THEN 'Pending Review'
                    WHEN 5 THEN 'Approved'
                    WHEN 27 THEN 'Archived'
                    ELSE 'Other (' + CAST(e.Status AS VARCHAR) + ')'
                END as status,
                COUNT(*) as count,
                ROUND(AVG(CAST(e.Duration AS FLOAT)), 2) as avg_duration
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
    
    "complex_year_comparison": {
        "id": "CMP_07",
        "intents": ["COMPARISON", "TREND"],
        "question_ar": "مقارنة سنوية",
        "question_en": "Year over year comparison",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) as year,
                COUNT(*) as inspections,
                COUNT(DISTINCT e.Location) as unique_locations,
                COUNT(DISTINCT e.ReporterID) as unique_inspectors,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score
            FROM Event e
            WHERE e.IsDeleted = 0
            GROUP BY YEAR(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate)
        """,
        "filters": {}
    },
    
    "complex_objection_analysis": {
        "id": "CMP_08",
        "intents": ["ANALYSIS", "FILTER"],
        "question_ar": "تحليل الاعتراضات",
        "question_en": "Objection analysis details",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE ev.ObjectionStatus
                    WHEN 0 THEN 'Pending'
                    WHEN 1 THEN 'Approved'
                    WHEN 2 THEN 'Rejected'
                    ELSE 'Unknown'
                END as objection_status,
                COUNT(*) as count,
                ROUND(AVG(ev.ViolationValue), 2) as avg_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND ev.HasObjection = 1
            {year_filter}
            GROUP BY ev.ObjectionStatus
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_top_violation_questions": {
        "id": "CMP_09",
        "intents": ["RANKING", "VIOLATION"],
        "question_ar": "أكثر أسئلة المخالفات شيوعاً",
        "question_en": "Top violation questions",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 15
                COALESCE(ev.QuestionNameEn, 'Unknown') as question,
                COUNT(*) as count,
                ROUND(AVG(ev.ViolationValue), 2) as avg_value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY ev.QuestionNameEn
            ORDER BY count DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_event_type_performance": {
        "id": "CMP_10",
        "intents": ["COMPARISON", "PERFORMANCE"],
        "question_ar": "أداء نوع الحدث",
        "question_en": "Event type performance comparison",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                COALESCE(et.Name, 'Unknown') as event_type,
                COUNT(*) as inspections,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                ROUND(AVG(CAST(e.Duration AS FLOAT)), 2) as avg_duration,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues
            FROM Event e
            LEFT JOIN EventType et ON e.EventType = et.Id
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY et.Name
            ORDER BY inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_inspector_efficiency": {
        "id": "CMP_11",
        "intents": ["RANKING", "EFFICIENCY"],
        "question_ar": "كفاءة المفتشين",
        "question_en": "Inspector efficiency ranking",
        "default_chart": "bar",
        "sql": """
            SELECT TOP 10
                e.ReporterID as inspector_id,
                COUNT(*) as inspections,
                ROUND(AVG(CAST(e.Duration AS FLOAT)), 2) as avg_duration,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                SUM(COALESCE(e.IssueCount, 0)) as issues_found,
                ROUND(CAST(SUM(COALESCE(e.IssueCount, 0)) AS FLOAT) / NULLIF(COUNT(*), 0), 2) as issues_per_inspection
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.ReporterID IS NOT NULL
            {year_filter}
            GROUP BY e.ReporterID
            HAVING COUNT(*) >= 10
            ORDER BY inspections DESC
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "complex_quarterly_trend": {
        "id": "CMP_12",
        "intents": ["TREND", "SUMMARY"],
        "question_ar": "الاتجاه الربع سنوي",
        "question_en": "Quarterly performance trend",
        "default_chart": "bar",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-Q' + CAST(DATEPART(QUARTER, e.SubmitionDate) AS VARCHAR) as quarter,
                COUNT(*) as inspections,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                SUM(COALESCE(e.IssueCount, 0)) as issues
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY YEAR(e.SubmitionDate), DATEPART(QUARTER, e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), DATEPART(QUARTER, e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    }
}
