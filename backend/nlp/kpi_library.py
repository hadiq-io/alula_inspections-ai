"""
KPI Library
============
10 core KPIs for AlUla inspection analytics.
Based on the existing ELM_AlulA_SQLDB implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


# KPI Definitions
KPI_DEFINITIONS = {
    "KPI_01": {
        "id": "KPI_01",
        "name_en": "Total Inspections",
        "name_ar": "إجمالي الفحوصات",
        "description_en": "Total number of inspections completed",
        "description_ar": "إجمالي عدد الفحوصات المكتملة",
        "unit": "count",
        "target": None,
        "sql": """
            SELECT COUNT(*) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_02": {
        "id": "KPI_02",
        "name_en": "Compliance Rate",
        "name_ar": "معدل الامتثال",
        "description_en": "Percentage of inspections with score >= 80",
        "description_ar": "نسبة الفحوصات التي حصلت على درجة 80 أو أعلى",
        "unit": "percentage",
        "target": 85.0,
        "sql": """
            SELECT 
                CAST(SUM(CASE WHEN Score >= 80 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_03": {
        "id": "KPI_03",
        "name_en": "Total Violations",
        "name_ar": "إجمالي المخالفات",
        "description_en": "Total number of violations recorded",
        "description_ar": "إجمالي عدد المخالفات المسجلة",
        "unit": "count",
        "target": None,
        "sql": """
            SELECT COUNT(*) as value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_04": {
        "id": "KPI_04",
        "name_en": "Average Score",
        "name_ar": "متوسط الدرجات",
        "description_en": "Average inspection score",
        "description_ar": "متوسط درجة الفحوصات",
        "unit": "score",
        "target": 80.0,
        "sql": """
            SELECT AVG(Score) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Score IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_05": {
        "id": "KPI_05",
        "name_en": "Active Inspectors",
        "name_ar": "المفتشين النشطين",
        "description_en": "Number of inspectors with at least one inspection",
        "description_ar": "عدد المفتشين الذين أجروا فحصًا واحدًا على الأقل",
        "unit": "count",
        "target": None,
        "sql": """
            SELECT COUNT(DISTINCT ReporterID) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.ReporterID IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_06": {
        "id": "KPI_06",
        "name_en": "Violation Value",
        "name_ar": "قيمة المخالفات",
        "description_en": "Total monetary value of violations",
        "description_ar": "إجمالي القيمة المالية للمخالفات",
        "unit": "currency",
        "target": None,
        "sql": """
            SELECT ISNULL(SUM(ev.ViolationValue), 0) as value
            FROM EventViolation ev
            JOIN Event e ON ev.EventId = e.Id
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_07": {
        "id": "KPI_07",
        "name_en": "Critical Issues",
        "name_ar": "المشاكل الحرجة",
        "description_en": "Total number of critical issues found",
        "description_ar": "إجمالي عدد المشاكل الحرجة المكتشفة",
        "unit": "count",
        "target": None,
        "sql": """
            SELECT ISNULL(SUM(CriticalIssueCount), 0) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_08": {
        "id": "KPI_08",
        "name_en": "Completion Rate",
        "name_ar": "معدل الإكمال",
        "description_en": "Percentage of inspections completed (closed status)",
        "description_ar": "نسبة الفحوصات المكتملة (الحالة مغلقة)",
        "unit": "percentage",
        "target": 95.0,
        "sql": """
            SELECT 
                CAST(SUM(CASE WHEN Status = 1 THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(*), 0) AS DECIMAL(5,2)) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND YEAR(e.SubmitionDate) = {year}
        """
    },
    "KPI_09": {
        "id": "KPI_09",
        "name_en": "High Risk Locations",
        "name_ar": "المواقع عالية المخاطر",
        "description_en": "Number of locations classified as high risk",
        "description_ar": "عدد المواقع المصنفة كعالية المخاطر",
        "unit": "count",
        "target": None,
        "sql": """
            SELECT COUNT(*) as value
            FROM ML_Location_Risk
            WHERE risk_category = 'HIGH'
        """
    },
    "KPI_10": {
        "id": "KPI_10",
        "name_en": "Avg Resolution Time",
        "name_ar": "متوسط وقت الحل",
        "description_en": "Average time to complete an inspection (minutes)",
        "description_ar": "متوسط الوقت لإكمال الفحص (دقائق)",
        "unit": "minutes",
        "target": 60.0,
        "sql": """
            SELECT AVG(CAST(Duration AS FLOAT)) as value
            FROM Event e
            WHERE e.IsDeleted = 0
              AND e.Duration > 0
              AND e.Duration IS NOT NULL
              AND YEAR(e.SubmitionDate) = {year}
        """
    }
}


class KPILibrary:
    """
    Provides access to KPI definitions and calculations.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.kpis = KPI_DEFINITIONS
    
    def get_kpi(self, kpi_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific KPI definition."""
        return self.kpis.get(kpi_id)
    
    def get_all_kpis(self) -> Dict[str, Dict[str, Any]]:
        """Get all KPI definitions."""
        return self.kpis
    
    def get_kpi_sql(self, kpi_id: str, year: Optional[int] = None) -> Optional[str]:
        """Get the SQL query for a specific KPI."""
        kpi = self.kpis.get(kpi_id)
        if not kpi:
            return None
        
        sql = kpi.get("sql", "")
        if year:
            sql = sql.replace("{year}", str(year))
        else:
            sql = sql.replace("{year}", str(datetime.now().year))
        
        return sql
    
    def get_kpi_by_name(self, name: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """Find a KPI by its name (English or Arabic)."""
        name_key = f"name_{language}"
        
        for kpi_id, kpi in self.kpis.items():
            if name.lower() in kpi.get(name_key, "").lower():
                return kpi
        
        return None
    
    def calculate_kpi(
        self, 
        kpi_id: str, 
        year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate a KPI value using the database connection.
        
        Returns:
            Dict with kpi info and calculated value, or None if not found
        """
        kpi = self.kpis.get(kpi_id)
        if not kpi or not self.db:
            return None
        
        sql = self.get_kpi_sql(kpi_id, year)
        
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            
            value = row[0] if row else None
            
            return {
                **kpi,
                "value": value,
                "calculated_at": datetime.now().isoformat(),
                "year": year or datetime.now().year
            }
        except Exception as e:
            return {
                **kpi,
                "value": None,
                "error": str(e),
                "calculated_at": datetime.now().isoformat()
            }
    
    def calculate_all_kpis(
        self, 
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Calculate all KPIs."""
        results = []
        for kpi_id in self.kpis.keys():
            result = self.calculate_kpi(kpi_id, year)
            if result:
                results.append(result)
        return results
    
    def get_kpi_trend(
        self, 
        kpi_id: str, 
        start_year: int, 
        end_year: int
    ) -> List[Dict[str, Any]]:
        """Calculate KPI values across multiple years for trend analysis."""
        trend = []
        for year in range(start_year, end_year + 1):
            result = self.calculate_kpi(kpi_id, year)
            if result:
                trend.append(result)
        return trend
