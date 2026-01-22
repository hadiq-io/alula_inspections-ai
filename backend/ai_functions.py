# backend/ai_functions.py
import pandas as pd
from typing import Dict, Any, List
from database import Database

class AIFunctions:
    """AI Agent Functions for SQL Database Queries"""
    
    def __init__(self):
        self.db = Database()
    
    def get_kpi_value(self, kpi_name: str) -> Dict[str, Any]:
        """Get KPI value using correct Event/EventViolation tables"""
        
        kpi_queries = {
            "total_inspections": """
                SELECT COUNT(DISTINCT Id) as value 
                FROM Event 
                WHERE IsDeleted = 0
            """,
            
            "compliance_rate": """
                WITH ComplianceStats AS (
                    SELECT 
                        COUNT(DISTINCT e.Id) AS TotalInspections,
                        COUNT(DISTINCT CASE WHEN v.EventId IS NULL THEN e.Id END) AS CompliantInspections
                    FROM Event e
                    LEFT JOIN EventViolation v ON e.Id = v.EventId
                    WHERE e.IsDeleted = 0
                )
                SELECT 
                    CAST(CompliantInspections * 100.0 / NULLIF(TotalInspections, 0) AS DECIMAL(5,2)) as value
                FROM ComplianceStats
            """,
            
            "total_violations": """
                SELECT COUNT(DISTINCT Id) as value 
                FROM EventViolation
            """,
            
            "inspector_count": """
                SELECT COUNT(DISTINCT CreatedBy) as value 
                FROM Event 
                WHERE CreatedBy IS NOT NULL AND IsDeleted = 0
            """,
            
            "avg_inspection_time": """
                SELECT AVG(CAST(InspectionDuration AS FLOAT)) as value 
                FROM Event 
                WHERE InspectionDuration IS NOT NULL AND IsDeleted = 0
            """,
            
            "open_violations": """
                SELECT COUNT(DISTINCT Id) as value 
                FROM EventViolation 
                WHERE ObjectionStatus = 1
            """,
            
            "high_severity_count": """
                SELECT COUNT(DISTINCT Id) as value 
                FROM EventViolation 
                WHERE Severity >= 3
            """,
            
            "repeat_violations": """
                SELECT COUNT(DISTINCT LicenseId) as value
                FROM (
                    SELECT e.LicenseId, COUNT(DISTINCT ev.Id) as ViolationCount
                    FROM Event e
                    INNER JOIN EventViolation ev ON e.Id = ev.EventId
                    WHERE e.IsDeleted = 0
                    GROUP BY e.LicenseId
                    HAVING COUNT(DISTINCT ev.Id) > 3
                ) AS RepeatOffenders
            """,
            
            "objection_rate": """
                WITH ObjectionStats AS (
                    SELECT 
                        COUNT(DISTINCT Id) AS TotalViolations,
                        COUNT(DISTINCT CASE WHEN HasObjection = 1 THEN Id END) AS ViolationsWithObjections
                    FROM EventViolation
                )
                SELECT 
                    CAST(ViolationsWithObjections * 100.0 / NULLIF(TotalViolations, 0) AS DECIMAL(5,2)) as value
                FROM ObjectionStats
            """,
            
            "avg_risk_score": """
                SELECT AVG(CAST(Severity AS FLOAT)) as value
                FROM EventViolation
                WHERE Severity IS NOT NULL
            """
        }
        
        try:
            query = kpi_queries.get(kpi_name)
            if not query:
                return {"error": f"Unknown KPI: {kpi_name}"}
            
            df = self.db.execute_query(query)
            
            if df.empty or df.iloc[0, 0] is None:
                return {"error": "No data found"}
            
            value = df.iloc[0, 0]
            
            # Format based on KPI type
            if kpi_name in ["compliance_rate", "objection_rate"]:
                formatted_value = f"{value:.1f}%"
            elif kpi_name == "avg_inspection_time":
                formatted_value = f"{value:.1f} mins"
            elif kpi_name == "avg_risk_score":
                formatted_value = f"{value:.2f}/5"
            else:
                formatted_value = f"{int(value):,}"
            
            return {
                "kpi": kpi_name.replace("_", " ").title(),
                "value": formatted_value,
                "raw_value": float(value),
                "chart_type": "metric"
            }
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def get_location_risk(self, top_n: int = 5) -> Dict[str, Any]:
        """Get high-risk locations"""
        
        query = f"""
            SELECT TOP {top_n}
                e.Region,
                e.City,
                COUNT(DISTINCT e.Id) AS TotalInspections,
                COUNT(DISTINCT ev.Id) AS TotalViolations,
                CAST(COUNT(DISTINCT ev.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.Id), 0) AS DECIMAL(10,2)) AS AvgViolationsPerInspection,
                SUM(CASE WHEN ev.Severity >= 3 THEN 1 ELSE 0 END) AS HighSeverityCount
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND e.Region IS NOT NULL
            GROUP BY e.Region, e.City
            ORDER BY TotalViolations DESC
        """
        
        try:
            df = self.db.execute_query(query)
            
            if df.empty:
                return {"error": "No location data found"}
            
            return {
                "data": df.to_dict('records'),
                "chart_type": "bar",
                "chart_config": {
                    "x_key": "City",
                    "y_key": "TotalViolations",
                    "title": "High-Risk Locations"
                }
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return {"error": str(e)}
    
    def get_inspector_stats(self, top_n: int = 5) -> Dict[str, Any]:
        """Get inspector performance"""
        
        query = f"""
            SELECT TOP {top_n}
                e.CreatedBy AS InspectorID,
                COUNT(DISTINCT e.Id) AS InspectionsCompleted,
                COUNT(DISTINCT ev.Id) AS ViolationsDetected,
                CAST(COUNT(DISTINCT ev.Id) * 1.0 / NULLIF(COUNT(DISTINCT e.Id), 0) AS DECIMAL(10,2)) AS AvgViolationsPerInspection
            FROM Event e
            LEFT JOIN EventViolation ev ON e.Id = ev.EventId
            WHERE e.IsDeleted = 0 AND e.CreatedBy IS NOT NULL
            GROUP BY e.CreatedBy
            ORDER BY InspectionsCompleted DESC
        """
        
        try:
            df = self.db.execute_query(query)
            
            if df.empty:
                return {"error": "No inspector data found"}
            
            return {
                "data": df.to_dict('records'),
                "chart_type": "bar",
                "chart_config": {
                    "x_key": "InspectorID",
                    "y_key": "InspectionsCompleted",
                    "title": "Inspector Performance"
                }
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return {"error": str(e)}
