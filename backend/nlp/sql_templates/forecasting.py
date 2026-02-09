"""
SQL Templates - Forecasting/ML Domain
======================================
Working templates for ML predictions and forecasting.
Uses ML_* tables if available, otherwise derived analytics.
"""

TEMPLATES = {
    "forecasting_inspection_trend": {
        "id": "FRC_01",
        "intents": ["TREND", "PREDICTION"],
        "question_ar": "توقعات التفتيشات المستقبلية",
        "question_en": "Inspection trend forecast",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) as year,
                CAST(MONTH(e.SubmitionDate) AS VARCHAR) as month,
                COUNT(*) as inspections
            FROM Event e
            WHERE e.IsDeleted = 0
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {}
    },
    
    "forecasting_violation_trend": {
        "id": "FRC_02",
        "intents": ["TREND", "PREDICTION"],
        "question_ar": "اتجاه المخالفات",
        "question_en": "Violation trend analysis",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(ev.Id) as violations
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {}
    },
    
    "forecasting_yearly_growth": {
        "id": "FRC_03",
        "intents": ["TREND", "COMPARISON"],
        "question_ar": "النمو السنوي",
        "question_en": "Year over year growth",
        "default_chart": "bar",
        "sql": """
            WITH yearly AS (
                SELECT 
                    YEAR(e.SubmitionDate) as year,
                    COUNT(*) as inspections
                FROM Event e
                WHERE e.IsDeleted = 0
                GROUP BY YEAR(e.SubmitionDate)
            )
            SELECT 
                CAST(year AS VARCHAR) as year,
                inspections,
                LAG(inspections) OVER (ORDER BY year) as prev_year,
                CASE 
                    WHEN LAG(inspections) OVER (ORDER BY year) IS NULL THEN 0
                    ELSE ROUND((CAST(inspections AS FLOAT) - LAG(inspections) OVER (ORDER BY year)) 
                         / LAG(inspections) OVER (ORDER BY year) * 100, 2)
                END as growth_percent
            FROM yearly
            ORDER BY year
        """,
        "filters": {}
    },
    
    "forecasting_workload_distribution": {
        "id": "FRC_04",
        "intents": ["DISTRIBUTION", "PREDICTION"],
        "question_ar": "توزيع حجم العمل",
        "question_en": "Workload distribution forecast",
        "default_chart": "bar",
        "sql": """
            SELECT 
                DATENAME(dw, e.SubmitionDate) as day_of_week,
                COUNT(*) as inspections,
                ROUND(AVG(CAST(e.Duration AS FLOAT)), 2) as avg_duration
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY DATENAME(dw, e.SubmitionDate), DATEPART(dw, e.SubmitionDate)
            ORDER BY DATEPART(dw, e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "forecasting_seasonal_pattern": {
        "id": "FRC_05",
        "intents": ["TREND", "PATTERN"],
        "question_ar": "النمط الموسمي",
        "question_en": "Seasonal inspection pattern",
        "default_chart": "line",
        "sql": """
            SELECT 
                DATENAME(month, e.SubmitionDate) as month_name,
                MONTH(e.SubmitionDate) as month_num,
                COUNT(*) as avg_inspections
            FROM Event e
            WHERE e.IsDeleted = 0
            {year_filter}
            GROUP BY DATENAME(month, e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY MONTH(e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    },
    
    "forecasting_issue_trend": {
        "id": "FRC_06",
        "intents": ["TREND", "PREDICTION"],
        "question_ar": "اتجاه المشكلات",
        "question_en": "Issue trend analysis",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                SUM(COALESCE(e.IssueCount, 0)) as total_issues,
                SUM(COALESCE(e.CriticalIssueCount, 0)) as critical_issues
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
    
    "forecasting_completion_rate": {
        "id": "FRC_07",
        "intents": ["TREND", "RATIO"],
        "question_ar": "معدل الإنجاز",
        "question_en": "Completion rate trend",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                COUNT(*) as total,
                SUM(CASE WHEN e.Status = 1 THEN 1 ELSE 0 END) as completed,
                ROUND(CAST(SUM(CASE WHEN e.Status = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as completion_rate
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
    
    "forecasting_score_trend": {
        "id": "FRC_08",
        "intents": ["TREND", "AVERAGE"],
        "question_ar": "اتجاه الدرجات",
        "question_en": "Score trend over time",
        "default_chart": "line",
        "sql": """
            SELECT 
                CAST(YEAR(e.SubmitionDate) AS VARCHAR) + '-' + RIGHT('0' + CAST(MONTH(e.SubmitionDate) AS VARCHAR), 2) as month,
                ROUND(AVG(CAST(e.Score AS FLOAT)), 2) as avg_score,
                MIN(e.Score) as min_score,
                MAX(e.Score) as max_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL
            {year_filter}
            GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ORDER BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
        """,
        "filters": {
            "year_filter": "AND YEAR(e.SubmitionDate) = {year}"
        }
    }
}
