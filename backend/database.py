# backend/database.py
import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.server = os.getenv('DB_SERVER', '20.3.236.169')
        self.port = int(os.getenv('DB_PORT', '1433'))
        self.database = os.getenv('DB_NAME', 'CHECK_ELM_AlUlaRC_DW')
        self.username = os.getenv('DB_USERNAME', 'sa')
        self.password = os.getenv('DB_PASSWORD', 'StrongPass123!')
    
    def get_connection(self):
        """Create database connection using pyodbc"""
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        return pyodbc.connect(conn_str, timeout=30)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"❌ Database error: {e}")
            return pd.DataFrame()
    
    def get_ml_summary(self) -> pd.DataFrame:
        """Get summary of all 9 ML models - FROM YOUR SQL FILE"""
        query = """
        SELECT 
            'KPI_01 & KPI_02' AS Model,
            'ML_Predictions' AS TableName,
            COUNT(*) AS RecordCount,
            MAX(generated_at) AS LastUpdated
        FROM ML_Predictions
        UNION ALL
        SELECT 'KPI_03', 'ML_Location_Risk', COUNT(*), MAX(generated_at) FROM ML_Location_Risk
        UNION ALL
        SELECT 'KPI_04', 'ML_Anomalies', COUNT(*), MAX(detected_at) FROM ML_Anomalies
        UNION ALL
        SELECT 'KPI_05', 'ML_Severity_Predictions', COUNT(*), MAX(predicted_at) FROM ML_Severity_Predictions
        UNION ALL
        SELECT 'KPI_06', 'ML_Scheduling_Recommendations', COUNT(*), MAX(generated_at) FROM ML_Scheduling_Recommendations
        UNION ALL
        SELECT 'KPI_07', 'ML_Objection_Predictions', COUNT(*), MAX(predicted_at) FROM ML_Objection_Predictions
        UNION ALL
        SELECT 'KPI_08', 'ML_Location_Clusters', COUNT(*), MAX(generated_at) FROM ML_Location_Clusters
        UNION ALL
        SELECT 'KPI_09', 'ML_Recurrence_Predictions', COUNT(*), MAX(predicted_at) FROM ML_Recurrence_Predictions
        UNION ALL
        SELECT 'KPI_10', 'ML_Inspector_Performance', COUNT(*), MAX(classified_at) FROM ML_Inspector_Performance
        ORDER BY Model
        """
        return self.execute_query(query)
    
    def get_high_risk_locations(self, limit: int = 20) -> pd.DataFrame:
        """Get high-risk locations - FROM YOUR SQL FILE"""
        query = f"""
        SELECT TOP {limit}
            mlr.location_id, 
            COALESCE(l.Name, 'Unknown Location ID: ' + CAST(mlr.location_id AS VARCHAR)) as location_name,
            COALESCE(l.NameAr, l.Name, 'موقع غير معروف') as location_name_ar,
            mlr.risk_probability, 
            mlr.risk_category,
            mlr.total_violations, 
            mlr.critical_violations,
            mlr.last_inspection_score, 
            mlr.days_since_inspection
        FROM ML_Location_Risk mlr
        LEFT JOIN Locations l ON mlr.location_id = l.Id
        ORDER BY mlr.risk_probability DESC
        """
        return self.execute_query(query)
    
    def get_inspector_performance(self) -> pd.DataFrame:
        """Get inspector performance"""
        query = """
        SELECT 
            inspector_id, total_inspections, avg_inspection_score,
            completion_rate, performance_score, predicted_label
        FROM ML_Inspector_Performance
        ORDER BY performance_score DESC
        """
        return self.execute_query(query)
    
    def get_anomalies(self, limit: int = 20) -> pd.DataFrame:
        """Get anomaly detections - FROM YOUR SQL FILE"""
        query = f"""
        SELECT TOP {limit}
            inspection_id, location_id, anomaly_probability,
            anomaly_type, score, duration_minutes, total_issues
        FROM ML_Anomalies
        ORDER BY anomaly_probability DESC
        """
        return self.execute_query(query)
    
    def get_recurrence_predictions(self, limit: int = 20) -> pd.DataFrame:
        """Get recurrence predictions - FROM YOUR SQL FILE"""
        query = f"""
        SELECT TOP {limit}
            question_id, event_id, location_id, severity,
            recurrence_probability, predicted_recurrence, actual_recurrence
        FROM ML_Recurrence_Predictions
        ORDER BY recurrence_probability DESC
        """
        return self.execute_query(query)
    
    def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total inspections
            cursor.execute("SELECT COUNT(*) FROM Event WHERE IsDeleted = 0")
            total_inspections = cursor.fetchone()[0]
            
            # Avg compliance
            cursor.execute("SELECT AVG(CAST(Score AS FLOAT)) FROM Event WHERE IsDeleted = 0")
            avg_score = cursor.fetchone()[0]
            
            # High-risk count
            cursor.execute("SELECT COUNT(*) FROM ML_Location_Risk WHERE risk_probability > 70")
            high_risk = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_inspections": total_inspections,
                "avg_compliance_score": round(float(avg_score), 2) if avg_score else 0,
                "high_risk_locations": high_risk,
                "active_ml_models": 9
            }
        except Exception as e:
            print(f"Error: {e}")
            return {"total_inspections": 0, "avg_compliance_score": 0, "high_risk_locations": 0, "active_ml_models": 9}