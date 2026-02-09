"""
ML Predictions Library
======================
9 ML prediction tables for AlUla inspection analytics.
Based on the existing ELM_AlulA_SQLDB implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


# ML Table Definitions
ML_TABLES = {
    "ML_Predictions": {
        "name": "ML_Predictions",
        "description_en": "Time-series forecasts for KPIs",
        "description_ar": "توقعات السلاسل الزمنية لمؤشرات الأداء",
        "columns": [
            "kpi_id", "kpi_name", "date", "actual_value", 
            "predicted_value", "confidence_lower", "confidence_upper"
        ],
        "sample_query": """
            SELECT TOP 30 * FROM ML_Predictions
            ORDER BY date DESC
        """
    },
    "ML_Location_Risk": {
        "name": "ML_Location_Risk",
        "description_en": "Location risk classification",
        "description_ar": "تصنيف مخاطر المواقع",
        "columns": [
            "location_id", "risk_probability", "risk_category",
            "total_violations", "critical_violations", "days_since_inspection"
        ],
        "sample_query": """
            SELECT TOP 20 * FROM ML_Location_Risk
            ORDER BY risk_probability DESC
        """
    },
    "ML_Inspector_Performance": {
        "name": "ML_Inspector_Performance",
        "description_en": "Inspector performance metrics and tiers",
        "description_ar": "مقاييس أداء المفتشين ومستوياتهم",
        "columns": [
            "inspector_id", "inspector_name", "total_inspections",
            "avg_score", "completion_rate", "performance_score", "performance_tier"
        ],
        "sample_query": """
            SELECT * FROM ML_Inspector_Performance
            ORDER BY performance_score DESC
        """
    },
    "ML_Anomalies": {
        "name": "ML_Anomalies",
        "description_en": "Detected inspection anomalies",
        "description_ar": "الانحرافات المكتشفة في الفحوصات",
        "columns": [
            "inspection_id", "location_id", "anomaly_type", "is_anomaly",
            "anomaly_probability", "score", "expected_score", 
            "duration_minutes", "total_issues"
        ],
        "sample_query": """
            SELECT TOP 20 * FROM ML_Anomalies
            WHERE is_anomaly = 1
            ORDER BY anomaly_probability DESC
        """
    },
    "ML_Severity_Predictions": {
        "name": "ML_Severity_Predictions",
        "description_en": "Violation severity predictions",
        "description_ar": "توقعات خطورة المخالفات",
        "columns": [
            "violation_id", "event_id", "question_name", 
            "actual_severity", "predicted_severity", "severity_confidence"
        ],
        "sample_query": """
            SELECT TOP 20 * FROM ML_Severity_Predictions
            ORDER BY predicted_severity DESC
        """
    },
    "ML_Objection_Predictions": {
        "name": "ML_Objection_Predictions",
        "description_en": "Objection outcome predictions",
        "description_ar": "توقعات نتائج الاعتراضات",
        "columns": [
            "violation_id", "event_id", "question_name", "severity",
            "violation_value", "predicted_outcome", 
            "approval_probability", "rejection_probability"
        ],
        "sample_query": """
            SELECT TOP 20 * FROM ML_Objection_Predictions
            ORDER BY approval_probability DESC
        """
    },
    "ML_Recurrence_Predictions": {
        "name": "ML_Recurrence_Predictions",
        "description_en": "Violation recurrence predictions",
        "description_ar": "توقعات تكرار المخالفات",
        "columns": [
            "event_id", "question_id", "question_name", "location_id",
            "recurrence_probability", "predicted_recurrence", "occurrence_number"
        ],
        "sample_query": """
            SELECT TOP 20 * FROM ML_Recurrence_Predictions
            WHERE recurrence_probability > 0.5
            ORDER BY recurrence_probability DESC
        """
    },
    "ML_Location_Clusters": {
        "name": "ML_Location_Clusters",
        "description_en": "Similar location clustering",
        "description_ar": "تجميع المواقع المتشابهة",
        "columns": [
            "location_id", "cluster_id", "cluster_name", "avg_score"
        ],
        "sample_query": """
            SELECT cluster_id, cluster_name, COUNT(*) as location_count
            FROM ML_Location_Clusters
            GROUP BY cluster_id, cluster_name
        """
    },
    "ML_Scheduling_Recommendations": {
        "name": "ML_Scheduling_Recommendations",
        "description_en": "Optimal inspection scheduling recommendations",
        "description_ar": "توصيات جدولة الفحوصات المثلى",
        "columns": [
            "location_id", "recommended_date", "recommended_hour",
            "optimal_score", "days_since_last_inspection"
        ],
        "sample_query": """
            SELECT TOP 20 * FROM ML_Scheduling_Recommendations
            ORDER BY optimal_score DESC
        """
    }
}


class MLPredictionsLibrary:
    """
    Provides access to ML prediction tables and queries.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.tables = ML_TABLES
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific ML table."""
        return self.tables.get(table_name)
    
    def get_all_tables(self) -> Dict[str, Dict[str, Any]]:
        """Get all ML table definitions."""
        return self.tables
    
    def query_table(
        self, 
        table_name: str, 
        limit: int = 20,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Query an ML table with optional filters.
        
        Returns:
            List of result rows as dictionaries
        """
        table_info = self.tables.get(table_name)
        if not table_info or not self.db:
            return None
        
        sql = f"SELECT TOP {limit} * FROM {table_name}"
        
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            return None
    
    def get_high_risk_locations(self, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Get locations classified as high risk."""
        if not self.db:
            return None
        
        sql = f"""
            SELECT TOP {limit}
                mlr.location_id, 
                COALESCE(l.Name, 'Unknown Location') as location_name,
                COALESCE(l.NameAr, l.Name) as location_name_ar,
                mlr.risk_probability, 
                mlr.risk_category,
                mlr.total_violations, 
                mlr.critical_violations,
                mlr.days_since_inspection
            FROM ML_Location_Risk mlr
            LEFT JOIN Locations l ON mlr.location_id = l.Id
            WHERE mlr.risk_category = 'HIGH'
            ORDER BY mlr.risk_probability DESC
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return None
    
    def get_top_performers(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get top performing inspectors."""
        return self.query_table(
            "ML_Inspector_Performance",
            limit=limit,
            where_clause="performance_tier = 'EXCELLENT'",
            order_by="performance_score DESC"
        )
    
    def get_anomalies(self, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Get detected anomalies."""
        return self.query_table(
            "ML_Anomalies",
            limit=limit,
            where_clause="is_anomaly = 1",
            order_by="anomaly_probability DESC"
        )
    
    def get_kpi_forecast(
        self, 
        kpi_id: str, 
        days: int = 30
    ) -> Optional[List[Dict[str, Any]]]:
        """Get forecast data for a specific KPI."""
        return self.query_table(
            "ML_Predictions",
            limit=days,
            where_clause=f"kpi_id = '{kpi_id}'",
            order_by="date DESC"
        )
    
    def get_recurrence_risks(
        self, 
        threshold: float = 0.5,
        limit: int = 20
    ) -> Optional[List[Dict[str, Any]]]:
        """Get violations with high recurrence probability."""
        return self.query_table(
            "ML_Recurrence_Predictions",
            limit=limit,
            where_clause=f"recurrence_probability > {threshold}",
            order_by="recurrence_probability DESC"
        )
    
    def get_scheduling_recommendations(
        self, 
        limit: int = 20
    ) -> Optional[List[Dict[str, Any]]]:
        """Get optimal scheduling recommendations."""
        return self.query_table(
            "ML_Scheduling_Recommendations",
            limit=limit,
            order_by="optimal_score DESC"
        )
    
    def get_location_clusters(self) -> Optional[List[Dict[str, Any]]]:
        """Get location cluster summary."""
        if not self.db:
            return None
        
        sql = """
            SELECT 
                cluster_id, 
                cluster_name, 
                COUNT(*) as location_count,
                AVG(avg_score) as cluster_avg_score
            FROM ML_Location_Clusters
            GROUP BY cluster_id, cluster_name
            ORDER BY cluster_id
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return None
    
    def get_risk_distribution(self) -> Optional[Dict[str, int]]:
        """Get distribution of risk categories."""
        if not self.db:
            return None
        
        sql = """
            SELECT 
                risk_category,
                COUNT(*) as count
            FROM ML_Location_Risk
            GROUP BY risk_category
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            return {row[0]: row[1] for row in rows}
        except Exception:
            return None
    
    def get_performance_tier_distribution(self) -> Optional[Dict[str, int]]:
        """Get distribution of inspector performance tiers."""
        if not self.db:
            return None
        
        sql = """
            SELECT 
                performance_tier,
                COUNT(*) as count
            FROM ML_Inspector_Performance
            GROUP BY performance_tier
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            return {row[0]: row[1] for row in rows}
        except Exception:
            return None
