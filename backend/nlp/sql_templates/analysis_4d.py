"""
4D Analysis Templates - Phase 3
================================
50 templates for multi-dimensional data analysis:
- Correlation Analysis (15) - Finding relationships between metrics
- Anomaly Detection (12) - Identifying unusual patterns
- Comparative Analysis (12) - Comparing dimensions
- Predictive/Causal (11) - Why and what next
"""

TEMPLATES = {
    # ============================================================================
    # CORRELATION ANALYSIS (15 templates)
    # ============================================================================
    
    "COR_01": {
        "id": "COR_01",
        "name_en": "Violations vs Inspector Workload Correlation",
        "name_ar": "ارتباط المخالفات بحجم عمل المفتش",
        "intents": ["CORRELATION", "ANALYSIS", "inspector", "workload"],
        "dimensions": ["what:violations", "who:inspector"],
        "default_chart": "scatter",
        "sql": """
            SELECT 
                e.ReporterID as inspector_id,
                COUNT(DISTINCT e.Id) as total_inspections,
                COUNT(DISTINCT ev.Id) as violations_found,
                CAST(COUNT(DISTINCT ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) * 100 as violation_rate
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY e.ReporterID
            HAVING COUNT(DISTINCT e.Id) >= 10
            ORDER BY total_inspections DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_02": {
        "id": "COR_02",
        "name_en": "Location Type vs Violation Severity",
        "name_ar": "نوع الموقع مقابل خطورة المخالفة",
        "intents": ["CORRELATION", "severity", "location type"],
        "dimensions": ["what:violations", "where:location_type", "what:severity"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                lt.Name as location_type, lt.NameAr as location_type_ar,
                COUNT(ev.Id) as total_violations,
                SUM(CASE WHEN ev.Severity >= 3 THEN 1 ELSE 0 END) as critical_violations,
                CAST(SUM(CASE WHEN ev.Severity >= 3 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(ev.Id), 0) * 100 as critical_rate
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY lt.Id, lt.Name, lt.NameAr
            ORDER BY critical_rate DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_03": {
        "id": "COR_03",
        "name_en": "Inspection Duration vs Quality Score",
        "name_ar": "مدة التفتيش مقابل جودة النتيجة",
        "intents": ["CORRELATION", "duration", "quality", "score"],
        "dimensions": ["what:duration", "what:score"],
        "default_chart": "scatter",
        "sql": """
            SELECT 
                CASE 
                    WHEN e.Duration < 30 THEN 'Under 30 min'
                    WHEN e.Duration < 60 THEN '30-60 min'
                    WHEN e.Duration < 120 THEN '1-2 hours'
                    ELSE 'Over 2 hours'
                END as duration_range,
                COUNT(*) as inspection_count,
                AVG(e.Score) as avg_score,
                AVG(e.IssueCount) as avg_issues_found
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Duration IS NOT NULL AND e.Score IS NOT NULL {year_filter}
            GROUP BY CASE 
                WHEN e.Duration < 30 THEN 'Under 30 min'
                WHEN e.Duration < 60 THEN '30-60 min'
                WHEN e.Duration < 120 THEN '1-2 hours'
                ELSE 'Over 2 hours' END
            ORDER BY AVG(e.Score) DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_04": {
        "id": "COR_04",
        "name_en": "Monthly Violation Type Patterns",
        "name_ar": "أنماط أنواع المخالفات الشهرية",
        "intents": ["CORRELATION", "TREND", "monthly", "pattern"],
        "dimensions": ["what:violations", "when:month"],
        "default_chart": "line",
        "sql": """
            SELECT 
                MONTH(e.SubmitionDate) as month_num,
                DATENAME(MONTH, e.SubmitionDate) as month_name,
                COUNT(*) as violation_count,
                COUNT(DISTINCT ev.QuestionNameEn) as unique_types
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY MONTH(e.SubmitionDate), DATENAME(MONTH, e.SubmitionDate)
            ORDER BY month_num
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_05": {
        "id": "COR_05",
        "name_en": "Repeat Violations by Location",
        "name_ar": "المخالفات المتكررة حسب الموقع",
        "intents": ["CORRELATION", "PATTERN", "repeat", "recurring"],
        "dimensions": ["what:violations", "where:location"],
        "default_chart": "bar",
        "sql": """
            SELECT TOP 20
                l.Name as location_name, l.NameAr as location_name_ar,
                COUNT(DISTINCT e.Id) as inspection_count,
                COUNT(ev.Id) as total_violations,
                CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) as violations_per_inspection
            FROM Event e
            JOIN Locations l ON e.Location = l.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY l.Id, l.Name, l.NameAr
            HAVING COUNT(ev.Id) > 5
            ORDER BY violations_per_inspection DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_06": {
        "id": "COR_06",
        "name_en": "Day of Week Impact Analysis",
        "name_ar": "تحليل تأثير يوم الأسبوع",
        "intents": ["CORRELATION", "PATTERN", "weekday", "daily"],
        "dimensions": ["what:inspections", "when:day"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                DATENAME(WEEKDAY, e.SubmitionDate) as day_name,
                DATEPART(WEEKDAY, e.SubmitionDate) as day_num,
                COUNT(DISTINCT e.Id) as inspections,
                COUNT(ev.Id) as violations,
                CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) as violations_per_inspection
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY DATENAME(WEEKDAY, e.SubmitionDate), DATEPART(WEEKDAY, e.SubmitionDate)
            ORDER BY day_num
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_07": {
        "id": "COR_07",
        "name_en": "Objection Rate by Violation Type",
        "name_ar": "معدل الاعتراض حسب نوع المخالفة",
        "intents": ["CORRELATION", "objection", "contested"],
        "dimensions": ["what:objections", "what:violations"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                ev.QuestionNameEn as violation_type,
                COUNT(*) as total_violations,
                SUM(CASE WHEN ev.HasObjection = 1 THEN 1 ELSE 0 END) as objections,
                CAST(SUM(CASE WHEN ev.HasObjection = 1 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 as objection_rate
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY ev.QuestionNameEn
            HAVING COUNT(*) >= 10
            ORDER BY objection_rate DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_08": {
        "id": "COR_08",
        "name_en": "Critical Issues vs Overall Score",
        "name_ar": "المشاكل الحرجة مقابل الدرجة الإجمالية",
        "intents": ["CORRELATION", "critical", "score", "impact"],
        "dimensions": ["what:critical", "what:score"],
        "default_chart": "scatter",
        "sql": """
            SELECT 
                e.CriticalIssueCount as critical_issues,
                COUNT(*) as inspection_count,
                AVG(e.Score) as avg_score,
                MIN(e.Score) as min_score, MAX(e.Score) as max_score
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL AND e.CriticalIssueCount IS NOT NULL {year_filter}
            GROUP BY e.CriticalIssueCount
            ORDER BY e.CriticalIssueCount
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_09": {
        "id": "COR_09",
        "name_en": "Seasonal Inspection Patterns",
        "name_ar": "أنماط التفتيش الموسمية",
        "intents": ["CORRELATION", "SEASONAL", "season"],
        "dimensions": ["what:inspections", "when:season"],
        "default_chart": "area",
        "sql": """
            SELECT 
                CASE 
                    WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(DISTINCT e.Id) as inspections,
                COUNT(ev.Id) as violations,
                AVG(e.Score) as avg_score
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY CASE 
                WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer'
                ELSE 'Fall' END
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_10": {
        "id": "COR_10",
        "name_en": "Severity Distribution by Location Type",
        "name_ar": "توزيع الخطورة حسب نوع الموقع",
        "intents": ["CORRELATION", "DISTRIBUTION", "severity"],
        "dimensions": ["what:severity", "where:location_type"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                lt.Name as location_type,
                SUM(CASE WHEN ev.Severity = 1 THEN 1 ELSE 0 END) as low_severity,
                SUM(CASE WHEN ev.Severity = 2 THEN 1 ELSE 0 END) as medium_severity,
                SUM(CASE WHEN ev.Severity >= 3 THEN 1 ELSE 0 END) as high_severity,
                COUNT(*) as total
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY lt.Id, lt.Name
            ORDER BY high_severity DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_11": {
        "id": "COR_11",
        "name_en": "Inspector Coverage vs Area Violations",
        "name_ar": "تغطية المفتش مقابل مخالفات المنطقة",
        "intents": ["CORRELATION", "SPATIAL", "coverage"],
        "dimensions": ["who:inspector", "where:area"],
        "default_chart": "scatter",
        "sql": """
            SELECT TOP 30
                l.Name as location_name,
                COUNT(DISTINCT e.ReporterID) as unique_inspectors,
                COUNT(DISTINCT e.Id) as total_inspections,
                COUNT(ev.Id) as total_violations,
                CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) as violations_per_inspection
            FROM Event e
            JOIN Locations l ON e.Location = l.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY l.Id, l.Name
            HAVING COUNT(DISTINCT e.Id) >= 5
            ORDER BY unique_inspectors DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_12": {
        "id": "COR_12",
        "name_en": "Time of Month Patterns",
        "name_ar": "أنماط وقت الشهر",
        "intents": ["CORRELATION", "PATTERN", "monthly"],
        "dimensions": ["what:inspections", "when:time_of_month"],
        "default_chart": "line",
        "sql": """
            SELECT 
                CASE 
                    WHEN DAY(e.SubmitionDate) <= 10 THEN 'Beginning (1-10)'
                    WHEN DAY(e.SubmitionDate) <= 20 THEN 'Middle (11-20)'
                    ELSE 'End (21-31)'
                END as period,
                COUNT(DISTINCT e.Id) as inspections,
                COUNT(ev.Id) as violations,
                AVG(e.Score) as avg_score
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY CASE 
                WHEN DAY(e.SubmitionDate) <= 10 THEN 'Beginning (1-10)'
                WHEN DAY(e.SubmitionDate) <= 20 THEN 'Middle (11-20)'
                ELSE 'End (21-31)' END
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_13": {
        "id": "COR_13",
        "name_en": "Compliance Score Factors",
        "name_ar": "عوامل درجة الامتثال",
        "intents": ["CORRELATION", "ANALYSIS", "compliance", "factors"],
        "dimensions": ["what:compliance", "what:factors"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                lt.Name as location_type,
                AVG(e.Score) as avg_score,
                AVG(e.Duration) as avg_duration,
                AVG(e.IssueCount) as avg_issues,
                AVG(e.CriticalIssueCount) as avg_critical,
                COUNT(*) as sample_size
            FROM Event e
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL {year_filter}
            GROUP BY lt.Id, lt.Name
            HAVING COUNT(*) >= 10
            ORDER BY avg_score DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_14": {
        "id": "COR_14",
        "name_en": "Location Density vs Violation Rate",
        "name_ar": "كثافة المواقع مقابل معدل المخالفات",
        "intents": ["CORRELATION", "SPATIAL", "density"],
        "dimensions": ["where:location", "what:density"],
        "default_chart": "scatter",
        "sql": """
            WITH LocationCounts AS (
                SELECT lt.Name as location_type, COUNT(DISTINCT l.Id) as location_count
                FROM Locations l JOIN LocationType lt ON l.LocationType = lt.Id
                WHERE l.Isdeleted = 0 GROUP BY lt.Id, lt.Name
            ),
            ViolationCounts AS (
                SELECT lt.Name as location_type, COUNT(ev.Id) as violation_count
                FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id
                JOIN Locations l ON e.Location = l.Id JOIN LocationType lt ON l.LocationType = lt.Id
                WHERE e.IsDeleted = 0 {year_filter} GROUP BY lt.Id, lt.Name
            )
            SELECT lc.location_type, lc.location_count, ISNULL(vc.violation_count, 0) as violation_count,
                CAST(ISNULL(vc.violation_count, 0) AS FLOAT) / NULLIF(lc.location_count, 0) as violations_per_location
            FROM LocationCounts lc LEFT JOIN ViolationCounts vc ON lc.location_type = vc.location_type
            ORDER BY violations_per_location DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "COR_15": {
        "id": "COR_15",
        "name_en": "Inspector Experience vs Performance",
        "name_ar": "خبرة المفتش مقابل الأداء",
        "intents": ["CORRELATION", "ANALYSIS", "experience", "performance"],
        "dimensions": ["who:inspector", "what:performance"],
        "default_chart": "scatter",
        "sql": """
            WITH InspectorStats AS (
                SELECT e.ReporterID, MIN(e.SubmitionDate) as first_inspection,
                    MAX(e.SubmitionDate) as last_inspection,
                    COUNT(*) as total_inspections, AVG(e.Score) as avg_score
                FROM Event e WHERE e.IsDeleted = 0 GROUP BY e.ReporterID
            )
            SELECT ReporterID as inspector_id,
                DATEDIFF(MONTH, first_inspection, last_inspection) as months_active,
                total_inspections, avg_score,
                CAST(total_inspections AS FLOAT) / NULLIF(DATEDIFF(MONTH, first_inspection, last_inspection) + 1, 0) as inspections_per_month
            FROM InspectorStats WHERE total_inspections >= 20
            ORDER BY months_active DESC
        """,
        "filters": {}
    },

    # ============================================================================
    # ANOMALY DETECTION (12 templates)
    # ============================================================================
    
    "ANO_01": {
        "id": "ANO_01",
        "name_en": "Violation Spikes Detection",
        "name_ar": "اكتشاف ارتفاعات المخالفات",
        "intents": ["ANOMALY", "SPIKE", "unusual", "spike"],
        "dimensions": ["what:violations", "when:spike"],
        "default_chart": "line",
        "sql": """
            WITH MonthlyViolations AS (
                SELECT YEAR(e.SubmitionDate) as year, MONTH(e.SubmitionDate) as month,
                    DATENAME(MONTH, e.SubmitionDate) as month_name, COUNT(ev.Id) as violations
                FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0 GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate), DATENAME(MONTH, e.SubmitionDate)
            ),
            Stats AS (SELECT AVG(violations) as avg_v, STDEV(violations) as std_v FROM MonthlyViolations)
            SELECT mv.year, mv.month, mv.month_name, mv.violations, s.avg_v as average,
                CASE WHEN mv.violations > s.avg_v + 2 * s.std_v THEN 'High Anomaly'
                     WHEN mv.violations > s.avg_v + s.std_v THEN 'Elevated'
                     WHEN mv.violations < s.avg_v - s.std_v THEN 'Low Anomaly' ELSE 'Normal' END as status
            FROM MonthlyViolations mv, Stats s ORDER BY mv.year DESC, mv.month DESC
        """,
        "filters": {}
    },
    
    "ANO_02": {
        "id": "ANO_02",
        "name_en": "Locations with Unusual Activity",
        "name_ar": "مواقع بنشاط غير عادي",
        "intents": ["ANOMALY", "SPATIAL", "unusual", "location"],
        "dimensions": ["where:location", "what:anomaly"],
        "default_chart": "bar",
        "sql": """
            WITH LocationStats AS (
                SELECT l.Name as location_name, COUNT(DISTINCT e.Id) as inspection_count,
                    COUNT(ev.Id) as violation_count, AVG(e.Score) as avg_score
                FROM Event e JOIN Locations l ON e.Location = l.Id
                LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0 {year_filter} GROUP BY l.Id, l.Name
            ),
            OverallStats AS (SELECT AVG(violation_count) as avg_v, STDEV(violation_count) as std_v FROM LocationStats)
            SELECT ls.location_name, ls.inspection_count, ls.violation_count, ls.avg_score,
                CASE WHEN ls.violation_count > os.avg_v + 2 * os.std_v THEN 'High Risk'
                     WHEN ls.violation_count < os.avg_v - os.std_v THEN 'Unusually Low' ELSE 'Normal' END as anomaly_status
            FROM LocationStats ls, OverallStats os
            WHERE ls.violation_count > os.avg_v + os.std_v OR ls.violation_count < os.avg_v - os.std_v
            ORDER BY ls.violation_count DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_03": {
        "id": "ANO_03",
        "name_en": "Inspector Performance Outliers",
        "name_ar": "المفتشون ذوو الأداء المتطرف",
        "intents": ["ANOMALY", "PERFORMANCE", "outlier", "inspector"],
        "dimensions": ["who:inspector", "what:outlier"],
        "default_chart": "bar",
        "sql": """
            WITH InspectorStats AS (
                SELECT e.ReporterID as inspector_id, COUNT(DISTINCT e.Id) as inspections,
                    COUNT(ev.Id) as violations_found,
                    CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) as violation_rate
                FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0 {year_filter} GROUP BY e.ReporterID HAVING COUNT(DISTINCT e.Id) >= 10
            ),
            Stats AS (SELECT AVG(violation_rate) as avg_rate, STDEV(violation_rate) as std_rate FROM InspectorStats)
            SELECT i.inspector_id, i.inspections, i.violations_found, ROUND(i.violation_rate, 2) as violation_rate,
                CASE WHEN i.violation_rate > s.avg_rate + 2 * s.std_rate THEN 'High Detector'
                     WHEN i.violation_rate < s.avg_rate - s.std_rate THEN 'Low Detector' ELSE 'Normal' END as status
            FROM InspectorStats i, Stats s
            WHERE i.violation_rate > s.avg_rate + s.std_rate OR i.violation_rate < s.avg_rate - s.std_rate
            ORDER BY i.violation_rate DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_04": {
        "id": "ANO_04",
        "name_en": "Zero Violation Locations (Suspicious)",
        "name_ar": "مواقع بدون مخالفات (مشبوهة)",
        "intents": ["ANOMALY", "SUSPICIOUS", "zero", "clean"],
        "dimensions": ["where:location", "what:suspicious"],
        "default_chart": "bar",
        "sql": """
            SELECT l.Name as location_name, lt.Name as location_type,
                COUNT(DISTINCT e.Id) as inspection_count, COUNT(ev.Id) as violation_count, AVG(e.Score) as avg_score
            FROM Event e
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY l.Id, l.Name, lt.Id, lt.Name
            HAVING COUNT(DISTINCT e.Id) >= 10 AND COUNT(ev.Id) = 0
            ORDER BY inspection_count DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_05": {
        "id": "ANO_05",
        "name_en": "Duration Outliers",
        "name_ar": "شذوذ المدة الزمنية",
        "intents": ["ANOMALY", "DURATION", "time", "outlier"],
        "dimensions": ["what:duration", "what:outlier"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE 
                    WHEN e.Duration < 5 THEN 'Under 5 min (Suspiciously Short)'
                    WHEN e.Duration < 15 THEN 'Very Short (5-15 min)'
                    WHEN e.Duration > 300 THEN 'Over 5 hours (Unusually Long)'
                    WHEN e.Duration > 180 THEN 'Very Long (3-5 hours)'
                    ELSE 'Normal Range'
                END as duration_category,
                COUNT(*) as inspection_count, AVG(e.Duration) as avg_duration_minutes
            FROM Event e
            WHERE e.IsDeleted = 0 AND e.Duration IS NOT NULL {year_filter}
            GROUP BY CASE 
                WHEN e.Duration < 5 THEN 'Under 5 min (Suspiciously Short)'
                WHEN e.Duration < 15 THEN 'Very Short (5-15 min)'
                WHEN e.Duration > 300 THEN 'Over 5 hours (Unusually Long)'
                WHEN e.Duration > 180 THEN 'Very Long (3-5 hours)'
                ELSE 'Normal Range' END
            ORDER BY inspection_count DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_06": {
        "id": "ANO_06",
        "name_en": "Score Distribution Anomalies",
        "name_ar": "شذوذ توزيع الدرجات",
        "intents": ["ANOMALY", "DISTRIBUTION", "score", "unusual"],
        "dimensions": ["what:score", "what:distribution"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE 
                    WHEN e.Score >= 90 THEN '90-100 (Excellent)'
                    WHEN e.Score >= 80 THEN '80-89 (Good)'
                    WHEN e.Score >= 70 THEN '70-79 (Fair)'
                    WHEN e.Score >= 60 THEN '60-69 (Poor)'
                    ELSE 'Below 60 (Critical)'
                END as score_range,
                COUNT(*) as count,
                ROUND(CAST(COUNT(*) AS FLOAT) * 100 / SUM(COUNT(*)) OVER(), 1) as percentage
            FROM Event e WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL {year_filter}
            GROUP BY CASE 
                WHEN e.Score >= 90 THEN '90-100 (Excellent)'
                WHEN e.Score >= 80 THEN '80-89 (Good)'
                WHEN e.Score >= 70 THEN '70-79 (Fair)'
                WHEN e.Score >= 60 THEN '60-69 (Poor)'
                ELSE 'Below 60 (Critical)' END
            ORDER BY MIN(e.Score) DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_07": {
        "id": "ANO_07",
        "name_en": "Perfect Score Locations (Suspicious)",
        "name_ar": "مواقع بدرجة كاملة (مشبوهة)",
        "intents": ["ANOMALY", "PERFECT", "suspicious", "100"],
        "dimensions": ["where:location", "what:score"],
        "default_chart": "bar",
        "sql": """
            SELECT l.Name as location_name, lt.Name as location_type,
                COUNT(*) as inspection_count,
                SUM(CASE WHEN e.Score = 100 THEN 1 ELSE 0 END) as perfect_scores,
                ROUND(CAST(SUM(CASE WHEN e.Score = 100 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 1) as perfect_rate
            FROM Event e
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL {year_filter}
            GROUP BY l.Id, l.Name, lt.Id, lt.Name
            HAVING COUNT(*) >= 5 AND SUM(CASE WHEN e.Score = 100 THEN 1 ELSE 0 END) >= 3
            ORDER BY perfect_rate DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_08": {
        "id": "ANO_08",
        "name_en": "Inactive Locations",
        "name_ar": "مواقع غير نشطة",
        "intents": ["ANOMALY", "INACTIVE", "dormant", "not inspected"],
        "dimensions": ["where:location", "when:last_inspection"],
        "default_chart": "bar",
        "sql": """
            SELECT l.Name as location_name, lt.Name as location_type,
                MAX(e.SubmitionDate) as last_inspection,
                DATEDIFF(DAY, MAX(e.SubmitionDate), GETDATE()) as days_since_inspection,
                COUNT(*) as total_inspections
            FROM Locations l
            JOIN LocationType lt ON l.LocationType = lt.Id
            LEFT JOIN Event e ON l.Id = e.Location
            WHERE l.Isdeleted = 0 AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, lt.Id, lt.Name
            HAVING DATEDIFF(DAY, MAX(e.SubmitionDate), GETDATE()) > 90 OR MAX(e.SubmitionDate) IS NULL
            ORDER BY days_since_inspection DESC
        """,
        "filters": {}
    },
    
    "ANO_09": {
        "id": "ANO_09",
        "name_en": "Sudden Compliance Changes",
        "name_ar": "تغييرات الامتثال المفاجئة",
        "intents": ["ANOMALY", "CHANGE", "sudden", "compliance"],
        "dimensions": ["what:compliance", "when:change"],
        "default_chart": "bar",
        "sql": """
            WITH MonthlyCompliance AS (
                SELECT YEAR(e.SubmitionDate) as year, MONTH(e.SubmitionDate) as month,
                    l.Name as location_name, AVG(e.Score) as avg_score, COUNT(*) as inspection_count
                FROM Event e JOIN Locations l ON e.Location = l.Id
                WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL
                GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate), l.Id, l.Name
                HAVING COUNT(*) >= 3
            ),
            ScoreChanges AS (
                SELECT location_name, year, month, avg_score,
                    LAG(avg_score) OVER (PARTITION BY location_name ORDER BY year, month) as prev_score
                FROM MonthlyCompliance
            )
            SELECT location_name, year, month, ROUND(avg_score, 1) as current_score,
                ROUND(prev_score, 1) as previous_score, ROUND(avg_score - prev_score, 1) as change,
                CASE WHEN avg_score - prev_score > 15 THEN 'Major Improvement'
                     WHEN avg_score - prev_score < -15 THEN 'Major Decline' ELSE 'Moderate Change' END as change_type
            FROM ScoreChanges WHERE ABS(avg_score - prev_score) > 10
            ORDER BY ABS(avg_score - prev_score) DESC
        """,
        "filters": {}
    },
    
    "ANO_10": {
        "id": "ANO_10",
        "name_en": "Weekend vs Weekday Anomalies",
        "name_ar": "شذوذ عطلة نهاية الأسبوع مقابل أيام الأسبوع",
        "intents": ["ANOMALY", "TEMPORAL", "weekend", "weekday"],
        "dimensions": ["when:day_type", "what:pattern"],
        "default_chart": "bar",
        "sql": """
            SELECT 
                CASE WHEN DATEPART(WEEKDAY, e.SubmitionDate) IN (6, 7) THEN 'Weekend' ELSE 'Weekday' END as day_type,
                COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations,
                AVG(e.Score) as avg_score, AVG(e.Duration) as avg_duration,
                CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) as violations_per_inspection
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY CASE WHEN DATEPART(WEEKDAY, e.SubmitionDate) IN (6, 7) THEN 'Weekend' ELSE 'Weekday' END
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_11": {
        "id": "ANO_11",
        "name_en": "Objection Rate Anomalies",
        "name_ar": "شذوذ معدل الاعتراض",
        "intents": ["ANOMALY", "OBJECTION", "contested", "unusual"],
        "dimensions": ["what:objections", "what:anomaly"],
        "default_chart": "bar",
        "sql": """
            WITH ViolationObjections AS (
                SELECT ev.QuestionNameEn as violation_type, COUNT(*) as total,
                    SUM(CASE WHEN ev.HasObjection = 1 THEN 1 ELSE 0 END) as objections,
                    CAST(SUM(CASE WHEN ev.HasObjection = 1 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 as objection_rate
                FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id
                WHERE e.IsDeleted = 0 {year_filter} GROUP BY ev.QuestionNameEn HAVING COUNT(*) >= 10
            ),
            Stats AS (SELECT AVG(objection_rate) as avg_rate, STDEV(objection_rate) as std_rate FROM ViolationObjections)
            SELECT vo.violation_type, vo.total, vo.objections, ROUND(vo.objection_rate, 1) as objection_rate,
                CASE WHEN vo.objection_rate > s.avg_rate + 2 * s.std_rate THEN 'Highly Contested'
                     WHEN vo.objection_rate < s.avg_rate - s.std_rate THEN 'Rarely Contested' ELSE 'Normal' END as status
            FROM ViolationObjections vo, Stats s
            WHERE vo.objection_rate > s.avg_rate + s.std_rate OR vo.objection_rate < s.avg_rate - s.std_rate
            ORDER BY vo.objection_rate DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "ANO_12": {
        "id": "ANO_12",
        "name_en": "Location Type Trend Anomalies",
        "name_ar": "شذوذ اتجاهات أنواع المواقع",
        "intents": ["ANOMALY", "TREND_CHANGE", "location type", "sudden"],
        "dimensions": ["where:location_type", "when:change"],
        "default_chart": "bar",
        "sql": """
            WITH MonthlyByType AS (
                SELECT lt.Name as location_type, YEAR(e.SubmitionDate) as year, MONTH(e.SubmitionDate) as month, COUNT(ev.Id) as violations
                FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id
                JOIN Locations l ON e.Location = l.Id JOIN LocationType lt ON l.LocationType = lt.Id
                WHERE e.IsDeleted = 0 GROUP BY lt.Id, lt.Name, YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ),
            TypeTrends AS (
                SELECT location_type, year, month, violations,
                    LAG(violations, 1) OVER (PARTITION BY location_type ORDER BY year, month) as prev_violations
                FROM MonthlyByType
            )
            SELECT location_type, year, month, violations as current_violations, prev_violations,
                violations - ISNULL(prev_violations, 0) as change,
                CASE WHEN prev_violations > 0 THEN ROUND((CAST(violations - prev_violations AS FLOAT) / prev_violations) * 100, 1) ELSE 0 END as percent_change
            FROM TypeTrends WHERE violations > prev_violations * 1.5 AND prev_violations > 5
            ORDER BY year DESC, month DESC, change DESC
        """,
        "filters": {}
    },

    # ============================================================================
    # COMPARATIVE ANALYSIS (12 templates)
    # ============================================================================
    
    "CMP_01": {
        "id": "CMP_01",
        "name_en": "Year over Year Comparison",
        "name_ar": "مقارنة سنة بسنة",
        "intents": ["COMPARISON", "TEMPORAL", "year", "yoy"],
        "dimensions": ["when:year", "what:metrics"],
        "default_chart": "bar",
        "sql": """
            SELECT YEAR(e.SubmitionDate) as year, COUNT(DISTINCT e.Id) as total_inspections,
                COUNT(ev.Id) as total_violations, ROUND(AVG(e.Score), 1) as avg_score,
                SUM(CASE WHEN e.Status = 1 THEN 1 ELSE 0 END) as completed
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) >= YEAR(GETDATE()) - 2
            GROUP BY YEAR(e.SubmitionDate) ORDER BY year DESC
        """,
        "filters": {}
    },
    
    "CMP_02": {
        "id": "CMP_02",
        "name_en": "Location Type Performance Comparison",
        "name_ar": "مقارنة أداء أنواع المواقع",
        "intents": ["COMPARISON", "LOCATION_TYPE", "performance"],
        "dimensions": ["where:location_type", "what:performance"],
        "default_chart": "bar",
        "sql": """
            SELECT lt.Name as location_type, lt.NameAr as location_type_ar,
                COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations,
                ROUND(AVG(e.Score), 1) as avg_score,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0), 2) as violations_per_inspection
            FROM Event e
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY lt.Id, lt.Name, lt.NameAr ORDER BY avg_score DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "CMP_03": {
        "id": "CMP_03",
        "name_en": "Inspector Performance Comparison",
        "name_ar": "مقارنة أداء المفتشين",
        "intents": ["COMPARISON", "INSPECTOR", "performance", "ranking"],
        "dimensions": ["who:inspector", "what:performance"],
        "default_chart": "bar",
        "sql": """
            SELECT TOP 15 e.ReporterID as inspector_id, COUNT(DISTINCT e.Id) as inspections,
                COUNT(ev.Id) as violations_found, ROUND(AVG(e.Duration), 0) as avg_duration_min,
                ROUND(AVG(e.Score), 1) as avg_location_score,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0), 2) as efficiency_score
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY e.ReporterID HAVING COUNT(DISTINCT e.Id) >= 20
            ORDER BY efficiency_score DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "CMP_04": {
        "id": "CMP_04",
        "name_en": "Monthly Trend Comparison",
        "name_ar": "مقارنة الاتجاهات الشهرية",
        "intents": ["COMPARISON", "TREND", "monthly"],
        "dimensions": ["when:month", "what:metrics"],
        "default_chart": "line",
        "sql": """
            SELECT MONTH(e.SubmitionDate) as month_num, DATENAME(MONTH, e.SubmitionDate) as month_name,
                YEAR(e.SubmitionDate) as year, COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) >= YEAR(GETDATE()) - 1
            GROUP BY MONTH(e.SubmitionDate), DATENAME(MONTH, e.SubmitionDate), YEAR(e.SubmitionDate)
            ORDER BY year, month_num
        """,
        "filters": {}
    },
    
    "CMP_05": {
        "id": "CMP_05",
        "name_en": "Quarter Comparison",
        "name_ar": "مقارنة الأرباع",
        "intents": ["COMPARISON", "QUARTERLY", "quarter"],
        "dimensions": ["when:quarter", "what:metrics"],
        "default_chart": "bar",
        "sql": """
            SELECT YEAR(e.SubmitionDate) as year, DATEPART(QUARTER, e.SubmitionDate) as quarter,
                CONCAT('Q', DATEPART(QUARTER, e.SubmitionDate)) as quarter_name,
                COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations, ROUND(AVG(e.Score), 1) as avg_score
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) >= YEAR(GETDATE()) - 1
            GROUP BY YEAR(e.SubmitionDate), DATEPART(QUARTER, e.SubmitionDate) ORDER BY year DESC, quarter
        """,
        "filters": {}
    },
    
    "CMP_06": {
        "id": "CMP_06",
        "name_en": "Violation Type Distribution",
        "name_ar": "توزيع أنواع المخالفات",
        "intents": ["COMPARISON", "VIOLATION_TYPE", "distribution"],
        "dimensions": ["what:violation_type", "what:count"],
        "default_chart": "pie",
        "sql": """
            SELECT TOP 10 ev.QuestionNameEn as violation_type, ev.QuestionNameAr as violation_type_ar,
                COUNT(*) as occurrence_count,
                ROUND(CAST(COUNT(*) AS FLOAT) * 100 / SUM(COUNT(*)) OVER(), 1) as percentage
            FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY ev.QuestionNameEn, ev.QuestionNameAr ORDER BY occurrence_count DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "CMP_07": {
        "id": "CMP_07",
        "name_en": "First Half vs Second Half",
        "name_ar": "النصف الأول مقابل النصف الثاني",
        "intents": ["COMPARISON", "BEFORE_AFTER", "half year"],
        "dimensions": ["when:period", "what:change"],
        "default_chart": "bar",
        "sql": """
            SELECT CASE WHEN e.SubmitionDate < DATEFROMPARTS({year}, 7, 1) THEN 'First Half' ELSE 'Second Half' END as period,
                COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations, ROUND(AVG(e.Score), 1) as avg_score,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0), 2) as violations_rate
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND YEAR(e.SubmitionDate) = {year}
            GROUP BY CASE WHEN e.SubmitionDate < DATEFROMPARTS({year}, 7, 1) THEN 'First Half' ELSE 'Second Half' END
        """,
        "filters": {}
    },
    
    "CMP_08": {
        "id": "CMP_08",
        "name_en": "Top vs Bottom Locations",
        "name_ar": "المواقع الأفضل مقابل الأسوأ",
        "intents": ["COMPARISON", "EXTREMES", "best", "worst"],
        "dimensions": ["where:location", "what:performance"],
        "default_chart": "bar",
        "sql": """
            WITH LocationScores AS (
                SELECT l.Name as location_name, AVG(e.Score) as avg_score, COUNT(DISTINCT e.Id) as inspections,
                    ROW_NUMBER() OVER (ORDER BY AVG(e.Score) DESC) as rank_best,
                    ROW_NUMBER() OVER (ORDER BY AVG(e.Score) ASC) as rank_worst
                FROM Event e JOIN Locations l ON e.Location = l.Id
                WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL {year_filter}
                GROUP BY l.Id, l.Name HAVING COUNT(DISTINCT e.Id) >= 5
            )
            SELECT location_name, ROUND(avg_score, 1) as avg_score, inspections,
                CASE WHEN rank_best <= 5 THEN 'Top 5' ELSE 'Bottom 5' END as category
            FROM LocationScores WHERE rank_best <= 5 OR rank_worst <= 5 ORDER BY avg_score DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "CMP_09": {
        "id": "CMP_09",
        "name_en": "Severity Level Comparison",
        "name_ar": "مقارنة مستويات الخطورة",
        "intents": ["COMPARISON", "SEVERITY", "level"],
        "dimensions": ["what:severity", "what:count"],
        "default_chart": "pie",
        "sql": """
            SELECT CASE WHEN ev.Severity = 1 THEN 'Low' WHEN ev.Severity = 2 THEN 'Medium'
                WHEN ev.Severity = 3 THEN 'High' WHEN ev.Severity >= 4 THEN 'Critical' ELSE 'Unknown' END as severity_level,
                COUNT(*) as count, ROUND(CAST(COUNT(*) AS FLOAT) * 100 / SUM(COUNT(*)) OVER(), 1) as percentage
            FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY CASE WHEN ev.Severity = 1 THEN 'Low' WHEN ev.Severity = 2 THEN 'Medium'
                WHEN ev.Severity = 3 THEN 'High' WHEN ev.Severity >= 4 THEN 'Critical' ELSE 'Unknown' END
            ORDER BY MIN(ev.Severity)
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "CMP_10": {
        "id": "CMP_10",
        "name_en": "Status Distribution",
        "name_ar": "توزيع الحالات",
        "intents": ["COMPARISON", "STATUS", "distribution"],
        "dimensions": ["what:status", "what:distribution"],
        "default_chart": "pie",
        "sql": """
            SELECT CASE e.Status WHEN 1 THEN 'Completed' WHEN 2 THEN 'In Progress' WHEN 3 THEN 'Pending'
                WHEN 5 THEN 'Approved' WHEN 27 THEN 'Archived' ELSE 'Other' END as status_name,
                COUNT(*) as count, ROUND(CAST(COUNT(*) AS FLOAT) * 100 / SUM(COUNT(*)) OVER(), 1) as percentage
            FROM Event e WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY e.Status ORDER BY count DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "CMP_11": {
        "id": "CMP_11",
        "name_en": "This Month vs Last Month",
        "name_ar": "هذا الشهر مقابل الشهر الماضي",
        "intents": ["COMPARISON", "MONTHLY", "current", "previous"],
        "dimensions": ["when:month", "what:metrics"],
        "default_chart": "bar",
        "sql": """
            SELECT CASE 
                WHEN YEAR(e.SubmitionDate) = YEAR(GETDATE()) AND MONTH(e.SubmitionDate) = MONTH(GETDATE()) THEN 'This Month'
                WHEN YEAR(e.SubmitionDate) = YEAR(DATEADD(MONTH, -1, GETDATE())) AND MONTH(e.SubmitionDate) = MONTH(DATEADD(MONTH, -1, GETDATE())) THEN 'Last Month'
                END as period,
                COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations, ROUND(AVG(e.Score), 1) as avg_score
            FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND (
                (YEAR(e.SubmitionDate) = YEAR(GETDATE()) AND MONTH(e.SubmitionDate) = MONTH(GETDATE()))
                OR (YEAR(e.SubmitionDate) = YEAR(DATEADD(MONTH, -1, GETDATE())) AND MONTH(e.SubmitionDate) = MONTH(DATEADD(MONTH, -1, GETDATE()))))
            GROUP BY CASE 
                WHEN YEAR(e.SubmitionDate) = YEAR(GETDATE()) AND MONTH(e.SubmitionDate) = MONTH(GETDATE()) THEN 'This Month'
                WHEN YEAR(e.SubmitionDate) = YEAR(DATEADD(MONTH, -1, GETDATE())) AND MONTH(e.SubmitionDate) = MONTH(DATEADD(MONTH, -1, GETDATE())) THEN 'Last Month' END
        """,
        "filters": {}
    },
    
    "CMP_12": {
        "id": "CMP_12",
        "name_en": "Objection Success Rate by Type",
        "name_ar": "معدل نجاح الاعتراض حسب النوع",
        "intents": ["COMPARISON", "OBJECTION", "success"],
        "dimensions": ["what:objection", "what:success"],
        "default_chart": "bar",
        "sql": """
            SELECT ev.QuestionNameEn as violation_type, COUNT(*) as total_objections,
                SUM(CASE WHEN ev.ObjectionStatus = 1 THEN 1 ELSE 0 END) as accepted,
                SUM(CASE WHEN ev.ObjectionStatus = 2 THEN 1 ELSE 0 END) as rejected,
                ROUND(CAST(SUM(CASE WHEN ev.ObjectionStatus = 1 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 1) as acceptance_rate
            FROM EventViolation ev JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0 AND ev.HasObjection = 1 {year_filter}
            GROUP BY ev.QuestionNameEn HAVING COUNT(*) >= 5 ORDER BY acceptance_rate DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },

    # ============================================================================
    # PREDICTIVE/CAUSAL ANALYSIS (11 templates)
    # ============================================================================
    
    "PRD_01": {
        "id": "PRD_01",
        "name_en": "High Risk Location Prediction",
        "name_ar": "توقع المواقع عالية المخاطر",
        "intents": ["PREDICTIVE", "RISK", "predict", "high risk"],
        "dimensions": ["where:location", "what:risk_factors"],
        "default_chart": "bar",
        "sql": """
            SELECT TOP 20 
                COALESCE(l.Name, 'Unknown Location') as location_name, 
                COALESCE(lt.Name, 'Unknown Type') as location_type,
                COUNT(DISTINCT e.Id) as inspection_history, 
                COUNT(ev.Id) as historical_violations,
                ROUND(CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0), 2) as violation_rate,
                SUM(CASE WHEN ev.Severity >= 3 THEN 1 ELSE 0 END) as critical_violations,
                DATEDIFF(DAY, MAX(e.SubmitionDate), GETDATE()) as days_since_inspection,
                CASE WHEN CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) > 1.5 THEN 'High Risk'
                     WHEN CAST(COUNT(ev.Id) AS FLOAT) / NULLIF(COUNT(DISTINCT e.Id), 0) > 0.8 THEN 'Medium Risk' ELSE 'Low Risk' END as risk_level
            FROM Event e
            LEFT JOIN Locations l ON e.Location = l.Id
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0
            GROUP BY e.Location, l.Name, l.LocationType, lt.Name HAVING COUNT(DISTINCT e.Id) >= 3
            ORDER BY violation_rate DESC
        """,
        "filters": {}
    },
    
    "PRD_02": {
        "id": "PRD_02",
        "name_en": "Violation Recurrence Prediction",
        "name_ar": "توقع تكرار المخالفات",
        "intents": ["PREDICTIVE", "RECURRENCE", "repeat", "likely"],
        "dimensions": ["where:location", "what:violations"],
        "default_chart": "bar",
        "sql": """
            WITH ViolationHistory AS (
                SELECT l.Name as location_name, e.SubmitionDate, COUNT(ev.Id) as violations_in_inspection
                FROM Event e JOIN Locations l ON e.Location = l.Id
                LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0 GROUP BY l.Id, l.Name, e.Id, e.SubmitionDate
            ),
            RecurrencePattern AS (
                SELECT location_name, COUNT(*) as total_inspections,
                    SUM(CASE WHEN violations_in_inspection > 0 THEN 1 ELSE 0 END) as inspections_with_violations,
                    AVG(CAST(violations_in_inspection AS FLOAT)) as avg_violations
                FROM ViolationHistory GROUP BY location_name HAVING COUNT(*) >= 3
            )
            SELECT TOP 15 location_name, total_inspections, inspections_with_violations,
                ROUND(CAST(inspections_with_violations AS FLOAT) / total_inspections * 100, 1) as recurrence_rate,
                ROUND(avg_violations, 2) as avg_violations_per_visit,
                CASE WHEN CAST(inspections_with_violations AS FLOAT) / total_inspections > 0.7 THEN 'High Recurrence Risk'
                     WHEN CAST(inspections_with_violations AS FLOAT) / total_inspections > 0.4 THEN 'Moderate Risk' ELSE 'Low Risk' END as prediction
            FROM RecurrencePattern ORDER BY recurrence_rate DESC
        """,
        "filters": {}
    },
    
    "PRD_03": {
        "id": "PRD_03",
        "name_en": "Compliance Trajectory Analysis",
        "name_ar": "تحليل مسار الامتثال",
        "intents": ["PREDICTIVE", "TRAJECTORY", "improving", "declining"],
        "dimensions": ["where:location", "what:compliance"],
        "default_chart": "line",
        "sql": """
            WITH MonthlyScores AS (
                SELECT l.Name as location_name, YEAR(e.SubmitionDate) as year, MONTH(e.SubmitionDate) as month,
                    AVG(e.Score) as avg_score
                FROM Event e JOIN Locations l ON e.Location = l.Id
                WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL AND e.SubmitionDate >= DATEADD(MONTH, -6, GETDATE())
                GROUP BY l.Id, l.Name, YEAR(e.SubmitionDate), MONTH(e.SubmitionDate)
            ),
            Trends AS (
                SELECT location_name, MIN(avg_score) as min_score, MAX(avg_score) as max_score, AVG(avg_score) as overall_avg,
                    (MAX(CASE WHEN year * 100 + month = (SELECT MAX(year * 100 + month) FROM MonthlyScores ms2 WHERE ms2.location_name = ms.location_name) THEN avg_score END) -
                     MIN(CASE WHEN year * 100 + month = (SELECT MIN(year * 100 + month) FROM MonthlyScores ms2 WHERE ms2.location_name = ms.location_name) THEN avg_score END)) as score_change
                FROM MonthlyScores ms GROUP BY location_name HAVING COUNT(*) >= 3
            )
            SELECT location_name, ROUND(overall_avg, 1) as average_score, ROUND(score_change, 1) as score_change_6mo,
                CASE WHEN score_change > 10 THEN 'Improving' WHEN score_change < -10 THEN 'Declining' ELSE 'Stable' END as trajectory,
                CASE WHEN score_change > 10 THEN 'Continue current approach' WHEN score_change < -10 THEN 'Needs intervention' ELSE 'Monitor closely' END as recommendation
            FROM Trends ORDER BY score_change DESC
        """,
        "filters": {}
    },
    
    "PRD_04": {
        "id": "PRD_04",
        "name_en": "Inspector Workload Optimization",
        "name_ar": "تحسين حجم عمل المفتش",
        "intents": ["PREDICTIVE", "OPTIMIZATION", "workload", "balance"],
        "dimensions": ["who:inspector", "what:workload"],
        "default_chart": "bar",
        "sql": """
            WITH InspectorMetrics AS (
                SELECT e.ReporterID as inspector_id, COUNT(DISTINCT e.Id) as inspections,
                    COUNT(ev.Id) as violations_found, AVG(e.Duration) as avg_duration, AVG(e.Score) as avg_location_score
                FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0 AND e.SubmitionDate >= DATEADD(MONTH, -3, GETDATE())
                GROUP BY e.ReporterID
            ),
            Stats AS (SELECT AVG(inspections) as avg_inspections, STDEV(inspections) as std_inspections FROM InspectorMetrics)
            SELECT im.inspector_id, im.inspections, im.violations_found,
                ROUND(CAST(im.violations_found AS FLOAT) / NULLIF(im.inspections, 0), 2) as efficiency,
                CASE WHEN im.inspections > s.avg_inspections + s.std_inspections THEN 'Overloaded'
                     WHEN im.inspections < s.avg_inspections - s.std_inspections THEN 'Underutilized' ELSE 'Optimal' END as workload_status,
                CASE WHEN im.inspections > s.avg_inspections + s.std_inspections THEN 'Reduce assignments'
                     WHEN im.inspections < s.avg_inspections - s.std_inspections THEN 'Increase assignments' ELSE 'Maintain current load' END as recommendation
            FROM InspectorMetrics im, Stats s ORDER BY im.inspections DESC
        """,
        "filters": {}
    },
    
    "PRD_05": {
        "id": "PRD_05",
        "name_en": "Seasonal Risk Forecast",
        "name_ar": "توقع المخاطر الموسمية",
        "intents": ["PREDICTIVE", "SEASONAL", "forecast", "expect"],
        "dimensions": ["when:season", "what:risk"],
        "default_chart": "line",
        "sql": """
            WITH HistoricalSeasons AS (
                SELECT CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer' ELSE 'Fall' END as season,
                    YEAR(e.SubmitionDate) as year, COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations, AVG(e.Score) as avg_score
                FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0
                GROUP BY CASE WHEN MONTH(e.SubmitionDate) IN (12, 1, 2) THEN 'Winter'
                    WHEN MONTH(e.SubmitionDate) IN (3, 4, 5) THEN 'Spring'
                    WHEN MONTH(e.SubmitionDate) IN (6, 7, 8) THEN 'Summer' ELSE 'Fall' END, YEAR(e.SubmitionDate)
            )
            SELECT season, AVG(inspections) as avg_inspections, AVG(violations) as avg_violations,
                ROUND(AVG(CAST(violations AS FLOAT) / NULLIF(inspections, 0)), 2) as expected_violation_rate,
                ROUND(AVG(avg_score), 1) as expected_avg_score,
                CASE WHEN AVG(CAST(violations AS FLOAT) / NULLIF(inspections, 0)) > 0.5 THEN 'High Staffing Needed' ELSE 'Normal Staffing' END as staffing_recommendation
            FROM HistoricalSeasons GROUP BY season ORDER BY expected_violation_rate DESC
        """,
        "filters": {}
    },
    
    "PRD_06": {
        "id": "PRD_06",
        "name_en": "Root Cause Analysis",
        "name_ar": "تحليل السبب الجذري",
        "intents": ["CAUSAL", "ROOT_CAUSE", "why", "cause"],
        "dimensions": ["what:violations", "why:cause"],
        "default_chart": "bar",
        "sql": """
            SELECT TOP 15 ev.QuestionNameEn as violation_type, lt.Name as common_location_type,
                COUNT(*) as occurrence_count, ROUND(AVG(e.Duration), 0) as avg_inspection_duration, ROUND(AVG(e.Score), 1) as avg_score,
                CASE WHEN COUNT(*) > 100 THEN 'Systemic Issue' WHEN COUNT(*) > 50 THEN 'Common Problem' ELSE 'Isolated Cases' END as issue_classification,
                CASE WHEN COUNT(*) > 100 THEN 'Policy/Training Review Needed' WHEN COUNT(*) > 50 THEN 'Targeted Intervention' ELSE 'Case-by-case handling' END as recommended_action
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            JOIN Locations l ON e.Location = l.Id
            JOIN LocationType lt ON l.LocationType = lt.Id
            WHERE e.IsDeleted = 0 {year_filter}
            GROUP BY ev.QuestionNameEn, lt.Name ORDER BY occurrence_count DESC
        """,
        "filters": {"year_filter": "AND YEAR(e.SubmitionDate) = {year}"}
    },
    
    "PRD_07": {
        "id": "PRD_07",
        "name_en": "Next Month Volume Forecast",
        "name_ar": "توقع حجم الشهر القادم",
        "intents": ["PREDICTIVE", "FORECAST", "next month", "expect"],
        "dimensions": ["when:future", "what:volume"],
        "default_chart": "line",
        "sql": """
            WITH MonthlyVolumes AS (
                SELECT YEAR(e.SubmitionDate) as year, MONTH(e.SubmitionDate) as month,
                    DATENAME(MONTH, e.SubmitionDate) as month_name,
                    COUNT(DISTINCT e.Id) as inspections, COUNT(ev.Id) as violations
                FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0 AND e.SubmitionDate >= DATEADD(MONTH, -12, GETDATE())
                GROUP BY YEAR(e.SubmitionDate), MONTH(e.SubmitionDate), DATENAME(MONTH, e.SubmitionDate)
            )
            SELECT year, month, month_name, inspections as actual_inspections, violations as actual_violations,
                AVG(inspections) OVER (ORDER BY year, month ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING) as moving_avg_inspections,
                'Historical' as data_type
            FROM MonthlyVolumes
            UNION ALL
            SELECT YEAR(DATEADD(MONTH, 1, GETDATE())) as year, MONTH(DATEADD(MONTH, 1, GETDATE())) as month,
                DATENAME(MONTH, DATEADD(MONTH, 1, GETDATE())) as month_name,
                NULL as actual_inspections, NULL as actual_violations,
                (SELECT AVG(inspections) FROM MonthlyVolumes WHERE year * 12 + month >= (SELECT MAX(year * 12 + month) - 2 FROM MonthlyVolumes)) as moving_avg_inspections,
                'Forecast' as data_type
            ORDER BY year, month
        """,
        "filters": {}
    },
    
    "PRD_08": {
        "id": "PRD_08",
        "name_en": "Priority Inspection Recommendations",
        "name_ar": "توصيات التفتيش ذات الأولوية",
        "intents": ["PREDICTIVE", "PRIORITY", "should inspect", "next"],
        "dimensions": ["where:location", "what:priority"],
        "default_chart": "bar",
        "sql": """
            WITH LocationRisk AS (
                SELECT l.Id as location_id, l.Name as location_name, lt.Name as location_type,
                    COUNT(DISTINCT e.Id) as historical_inspections, COUNT(ev.Id) as historical_violations,
                    MAX(e.SubmitionDate) as last_inspection,
                    DATEDIFF(DAY, MAX(e.SubmitionDate), GETDATE()) as days_since_inspection,
                    AVG(e.Score) as avg_score
                FROM Locations l
                JOIN LocationType lt ON l.LocationType = lt.Id
                LEFT JOIN Event e ON l.Id = e.Location
                LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE l.Isdeleted = 0 GROUP BY l.Id, l.Name, lt.Id, lt.Name
            )
            SELECT TOP 20 location_name, location_type, days_since_inspection, historical_violations, ROUND(avg_score, 1) as avg_score,
                CASE WHEN days_since_inspection > 180 OR days_since_inspection IS NULL THEN 100
                     WHEN historical_violations > 10 THEN 90 WHEN avg_score < 70 THEN 80
                     WHEN days_since_inspection > 90 THEN 60 ELSE 30 END as priority_score,
                CASE WHEN days_since_inspection > 180 OR days_since_inspection IS NULL THEN 'Overdue'
                     WHEN historical_violations > 10 THEN 'High Risk History' WHEN avg_score < 70 THEN 'Low Compliance'
                     WHEN days_since_inspection > 90 THEN 'Due Soon' ELSE 'Routine' END as reason
            FROM LocationRisk ORDER BY priority_score DESC, days_since_inspection DESC
        """,
        "filters": {}
    },
    
    "PRD_09": {
        "id": "PRD_09",
        "name_en": "Compliance Score Prediction",
        "name_ar": "توقع درجة الامتثال",
        "intents": ["PREDICTIVE", "SCORE", "expected", "predict"],
        "dimensions": ["where:location", "what:score"],
        "default_chart": "bar",
        "sql": """
            WITH LocationHistory AS (
                SELECT l.Name as location_name, lt.Name as location_type,
                    COUNT(DISTINCT e.Id) as inspection_count, AVG(e.Score) as avg_score, STDEV(e.Score) as score_volatility,
                    MIN(e.Score) as worst_score, MAX(e.Score) as best_score,
                    (SELECT TOP 1 Score FROM Event WHERE Location = l.Id AND IsDeleted = 0 ORDER BY SubmitionDate DESC) as last_score
                FROM Event e JOIN Locations l ON e.Location = l.Id JOIN LocationType lt ON l.LocationType = lt.Id
                WHERE e.IsDeleted = 0 AND e.Score IS NOT NULL
                GROUP BY l.Id, l.Name, lt.Id, lt.Name HAVING COUNT(DISTINCT e.Id) >= 3
            )
            SELECT TOP 20 location_name, location_type, ROUND(avg_score, 1) as historical_avg, ROUND(last_score, 1) as last_score,
                ROUND(avg_score * 0.6 + last_score * 0.4, 1) as predicted_next_score, ROUND(score_volatility, 1) as score_volatility,
                CASE WHEN score_volatility > 15 THEN 'Unpredictable' WHEN score_volatility > 8 THEN 'Variable' ELSE 'Consistent' END as predictability
            FROM LocationHistory ORDER BY predicted_next_score ASC
        """,
        "filters": {}
    },
    
    "PRD_10": {
        "id": "PRD_10",
        "name_en": "Resource Allocation Optimization",
        "name_ar": "تحسين توزيع الموارد",
        "intents": ["PREDICTIVE", "OPTIMIZATION", "resource", "allocate"],
        "dimensions": ["where:area", "what:resources"],
        "default_chart": "bar",
        "sql": """
            WITH AreaMetrics AS (
                SELECT lt.Name as area_type, COUNT(DISTINCT l.Id) as location_count,
                    COUNT(DISTINCT e.Id) as total_inspections, COUNT(ev.Id) as total_violations,
                    COUNT(DISTINCT e.ReporterID) as inspectors_assigned, AVG(e.Score) as avg_score
                FROM Locations l
                JOIN LocationType lt ON l.LocationType = lt.Id
                LEFT JOIN Event e ON l.Id = e.Location AND e.SubmitionDate >= DATEADD(MONTH, -6, GETDATE())
                LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE l.Isdeleted = 0 GROUP BY lt.Id, lt.Name
            )
            SELECT area_type, location_count, total_inspections, total_violations, inspectors_assigned,
                ROUND(CAST(total_inspections AS FLOAT) / NULLIF(location_count, 0), 1) as inspections_per_location,
                ROUND(CAST(total_violations AS FLOAT) / NULLIF(total_inspections, 0), 2) as violation_rate,
                CASE WHEN CAST(total_violations AS FLOAT) / NULLIF(total_inspections, 0) > 0.5 THEN 'Increase Coverage'
                     WHEN CAST(total_inspections AS FLOAT) / NULLIF(location_count, 0) > 5 THEN 'Reduce Coverage' ELSE 'Maintain Current' END as resource_recommendation
            FROM AreaMetrics ORDER BY violation_rate DESC
        """,
        "filters": {}
    },
    
    "PRD_11": {
        "id": "PRD_11",
        "name_en": "Year over Year Impact Analysis",
        "name_ar": "تحليل التأثير سنة بسنة",
        "intents": ["CAUSAL", "IMPACT", "effect", "intervention"],
        "dimensions": ["when:before_after", "what:impact"],
        "default_chart": "bar",
        "sql": """
            WITH YearlyMetrics AS (
                SELECT YEAR(e.SubmitionDate) as year, COUNT(DISTINCT e.Id) as inspections,
                    COUNT(ev.Id) as violations, AVG(e.Score) as avg_score,
                    SUM(CASE WHEN ev.Severity >= 3 THEN 1 ELSE 0 END) as critical_violations
                FROM Event e LEFT JOIN EventViolation ev ON e.Id = ev.EventId
                WHERE e.IsDeleted = 0 GROUP BY YEAR(e.SubmitionDate)
            )
            SELECT year, inspections, violations, ROUND(avg_score, 1) as avg_score, critical_violations,
                ROUND(CAST(violations AS FLOAT) / NULLIF(inspections, 0), 2) as violation_rate,
                LAG(ROUND(CAST(violations AS FLOAT) / NULLIF(inspections, 0), 2)) OVER (ORDER BY year) as prev_year_rate,
                CASE WHEN CAST(violations AS FLOAT) / NULLIF(inspections, 0) < LAG(CAST(violations AS FLOAT) / NULLIF(inspections, 0)) OVER (ORDER BY year) THEN 'Improved'
                     WHEN CAST(violations AS FLOAT) / NULLIF(inspections, 0) > LAG(CAST(violations AS FLOAT) / NULLIF(inspections, 0)) OVER (ORDER BY year) THEN 'Declined'
                     ELSE 'Stable' END as trend
            FROM YearlyMetrics ORDER BY year DESC
        """,
        "filters": {}
    },

    # =========================================================================
    # MAP / SPATIAL VISUALIZATION TEMPLATES (MAP_01 - MAP_06)
    # Uses location aggregation with simulated coordinates for AlUla area
    # AlUla center: 26.6174°N, 37.9236°E
    # =========================================================================
    "MAP_01": {
        "id": "MAP_01",
        "name_en": "Violations by Location Map",
        "name_ar": "خريطة المخالفات حسب الموقع",
        "intents": ["MAP", "SPATIAL", "LOCATION", "GEOGRAPHY"],
        "dimensions": ["location", "violations"],
        "keywords_en": ["map", "show on map", "location map", "violations map", "geographic", "where", "locations"],
        "keywords_ar": ["خريطة", "على الخريطة", "أين", "المواقع", "جغرافي"],
        "default_chart": "map",
        "colorBy": "violations",
        "sql": """
            SELECT TOP 20
                l.Name as name, 
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Lat as latitude,
                l.Long as longitude,
                COUNT(ev.Id) as violations,
                COUNT(DISTINCT e.Id) as inspections,
                ROUND(AVG(e.Score), 1) as score
            FROM Locations l
            LEFT JOIN Event e ON l.Id = e.Location
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE l.Isdeleted = 0 AND l.Lat IS NOT NULL AND l.Long IS NOT NULL AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, l.NameAr, l.Lat, l.Long
            HAVING COUNT(ev.Id) > 0
            ORDER BY violations DESC
        """,
        "filters": {}
    },
    "MAP_02": {
        "id": "MAP_02",
        "name_en": "High Risk Locations Map",
        "name_ar": "خريطة المواقع عالية المخاطر",
        "intents": ["MAP", "SPATIAL", "RISK", "HIGH_RISK"],
        "dimensions": ["location", "risk"],
        "keywords_en": ["high risk map", "risk locations", "dangerous locations", "high risk on map", "show risky"],
        "keywords_ar": ["خريطة المخاطر", "مواقع عالية المخاطر", "مواقع خطرة"],
        "default_chart": "map",
        "colorBy": "risk_level",
        "sql": """
            SELECT TOP 20
                l.Name as name, 
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Lat as latitude,
                l.Long as longitude,
                COUNT(ev.Id) as violations,
                ROUND(AVG(e.Score), 1) as score,
                CASE WHEN AVG(e.Score) < 50 THEN 'High'
                     WHEN AVG(e.Score) < 75 THEN 'Medium'
                     ELSE 'Low' END as risk_level
            FROM Locations l
            LEFT JOIN Event e ON l.Id = e.Location
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE l.Isdeleted = 0 AND l.Lat IS NOT NULL AND l.Long IS NOT NULL AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, l.NameAr, l.Lat, l.Long
            HAVING COUNT(DISTINCT e.Id) > 0
            ORDER BY score ASC
        """,
        "filters": {}
    },
    "MAP_03": {
        "id": "MAP_03",
        "name_en": "Compliance Score Map",
        "name_ar": "خريطة درجات الامتثال",
        "intents": ["MAP", "SPATIAL", "COMPLIANCE", "SCORE"],
        "dimensions": ["location", "score"],
        "keywords_en": ["compliance map", "score map", "compliance by location", "scores on map"],
        "keywords_ar": ["خريطة الامتثال", "درجات على الخريطة", "الامتثال حسب الموقع"],
        "default_chart": "map",
        "colorBy": "score",
        "sql": """
            SELECT TOP 20
                l.Name as name, 
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Lat as latitude,
                l.Long as longitude,
                COUNT(DISTINCT e.Id) as inspections,
                ROUND(AVG(e.Score), 1) as score,
                COUNT(ev.Id) as violations
            FROM Locations l
            LEFT JOIN Event e ON l.Id = e.Location
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE l.Isdeleted = 0 AND l.Lat IS NOT NULL AND l.Long IS NOT NULL AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, l.NameAr, l.Lat, l.Long
            HAVING COUNT(DISTINCT e.Id) > 0
            ORDER BY score DESC
        """,
        "filters": {}
    },
    "MAP_04": {
        "id": "MAP_04",
        "name_en": "All Locations Overview Map",
        "name_ar": "خريطة نظرة عامة على جميع المواقع",
        "intents": ["MAP", "SPATIAL", "OVERVIEW", "ALL"],
        "dimensions": ["location", "overview"],
        "keywords_en": ["all locations map", "show all on map", "overview map", "location overview", "all neighborhoods"],
        "keywords_ar": ["خريطة جميع المواقع", "نظرة عامة على الخريطة", "عرض الكل", "جميع الأحياء"],
        "default_chart": "map",
        "colorBy": "violations",
        "sql": """
            SELECT TOP 25
                l.Name as name, 
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Lat as latitude,
                l.Long as longitude,
                COALESCE(COUNT(DISTINCT e.Id), 0) as inspections,
                COALESCE(ROUND(AVG(e.Score), 1), 0) as score,
                COALESCE(COUNT(ev.Id), 0) as violations
            FROM Locations l
            LEFT JOIN Event e ON l.Id = e.Location
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE l.Isdeleted = 0 AND l.Lat IS NOT NULL AND l.Long IS NOT NULL AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, l.NameAr, l.Lat, l.Long
            ORDER BY violations DESC, name
        """,
        "filters": {}
    },
    "MAP_05": {
        "id": "MAP_05",
        "name_en": "Inspections by Location Map",
        "name_ar": "خريطة الفحوصات حسب الموقع",
        "intents": ["MAP", "SPATIAL", "INSPECTIONS"],
        "dimensions": ["location", "inspections"],
        "keywords_en": ["inspections map", "inspection locations", "where inspections", "inspections on map"],
        "keywords_ar": ["خريطة الفحوصات", "أين الفحوصات", "فحوصات على الخريطة"],
        "default_chart": "map",
        "colorBy": "inspections",
        "sql": """
            SELECT TOP 20
                l.Name as name, 
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Lat as latitude,
                l.Long as longitude,
                COUNT(DISTINCT e.Id) as inspections,
                ROUND(AVG(e.Score), 1) as score,
                COUNT(ev.Id) as violations
            FROM Locations l
            LEFT JOIN Event e ON l.Id = e.Location
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE l.Isdeleted = 0 AND l.Lat IS NOT NULL AND l.Long IS NOT NULL AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, l.NameAr, l.Lat, l.Long
            HAVING COUNT(DISTINCT e.Id) > 0
            ORDER BY inspections DESC
        """,
        "filters": {}
    },
    "MAP_06": {
        "id": "MAP_06",
        "name_en": "Activity Type Distribution Map",
        "name_ar": "خريطة توزيع أنواع الأنشطة",
        "intents": ["MAP", "SPATIAL", "ACTIVITY", "TYPE"],
        "dimensions": ["activity", "distribution"],
        "keywords_en": ["activity map", "business type map", "type distribution", "activity locations"],
        "keywords_ar": ["خريطة الأنشطة", "توزيع الأنشطة", "أنواع الأعمال"],
        "default_chart": "map",
        "colorBy": "violations",
        "sql": """
            SELECT TOP 15
                l.Name as name, 
                COALESCE(l.NameAr, l.Name) as name_ar,
                l.Lat as latitude,
                l.Long as longitude,
                lt.Name as activity_type,
                COUNT(DISTINCT e.Id) as inspections,
                ROUND(AVG(e.Score), 1) as score,
                COUNT(ev.Id) as violations
            FROM Locations l
            LEFT JOIN LocationType lt ON l.LocationType = lt.Id
            LEFT JOIN Event e ON l.Id = e.Location
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE l.Isdeleted = 0 AND l.Lat IS NOT NULL AND l.Long IS NOT NULL AND (e.IsDeleted = 0 OR e.Id IS NULL)
            GROUP BY l.Id, l.Name, l.NameAr, l.Lat, l.Long, lt.Name
            HAVING COUNT(DISTINCT e.Id) > 0
            ORDER BY violations DESC
        """,
        "filters": {}
    }
}

# Template category summary
TEMPLATE_SUMMARY = {
    "correlation": [f"COR_{i:02d}" for i in range(1, 16)],
    "anomaly": [f"ANO_{i:02d}" for i in range(1, 13)],
    "comparative": [f"CMP_{i:02d}" for i in range(1, 13)],
    "predictive": [f"PRD_{i:02d}" for i in range(1, 12)],
    "map": [f"MAP_{i:02d}" for i in range(1, 7)]
}

ANALYSIS_4D_CATEGORIES = {
    "correlation": {"name_en": "Correlation Analysis", "name_ar": "تحليل الارتباط", "count": 15, "icon": "link"},
    "anomaly": {"name_en": "Anomaly Detection", "name_ar": "اكتشاف الشذوذ", "count": 12, "icon": "alert-triangle"},
    "comparative": {"name_en": "Comparative Analysis", "name_ar": "التحليل المقارن", "count": 12, "icon": "bar-chart-2"},
    "predictive": {"name_en": "Predictive & Causal", "name_ar": "التنبؤي والسببي", "count": 11, "icon": "trending-up"},
    "map": {"name_en": "Spatial Visualization", "name_ar": "التصور المكاني", "count": 6, "icon": "map"}
}