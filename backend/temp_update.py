def get_high_risk_locations():
    """Query ML_Location_Risk table for high-risk heritage locations"""
    try:
        conn = get_db_connection()
        
        query = """
        SELECT TOP 10
            lr.location_id,
            l.Name AS LocationName,
            lr.risk_probability,
            lr.risk_category,
            lr.last_inspection_score,
            lr.days_since_inspection,
            lr.total_violations,
            lr.critical_violations,
            lr.training_accuracy,
            lr.generated_at
        FROM ML_Location_Risk lr
        LEFT JOIN Locations l ON lr.location_id = l.Id
        ORDER BY lr.risk_probability DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            return {
                "message": "No high-risk location data available from ML models.",
                "chart_data": None,
                "chart_type": None
            }
        
        # Format message with proper spacing and structure
        message = f"Top {len(df)} High-Risk Heritage Locations (ML Model KPI_03):\n\n"
        
        chart_data = []
        for idx, row in df.iterrows():
            location_name = row['LocationName'] if pd.notna(row['LocationName']) else f"Location {row['location_id']}"
            risk_score = float(row['risk_probability']) if row['risk_probability'] <= 100 else float(row['risk_probability']) / 100
            
            # Each location as a numbered item
            message += f"{idx+1}. {location_name}\n"
            
            # Indented details with proper spacing
            message += f"   - Risk Score: {risk_score:.1f}/100\n"
            message += f"   - Category: {row['risk_category']}\n"
            message += f"   - Last Inspection: {row['last_inspection_score']:.1f}/100\n"
            message += f"   - Days Since Inspection: {row['days_since_inspection']}\n"
            message += f"   - Total Violations: {row['total_violations']}\n"
            message += f"   - Critical Violations: {row['critical_violations']}\n"
            
            # Double newline to separate locations
            message += "\n"
            
            chart_data.append({
                "location": location_name[:30],
                "risk": float(risk_score),
                "violations": int(row['total_violations']),
                "critical": int(row['critical_violations'])
            })
        
        # Footer with metadata
        accuracy = df.iloc[0]['training_accuracy'] * 100 if df.iloc[0]['training_accuracy'] <= 1 else df.iloc[0]['training_accuracy']
        message += f"\n*ML Model Accuracy: {accuracy:.1f}%*\n"
        message += f"*Last Updated: {df.iloc[0]['generated_at'].strftime('%Y-%m-%d %H:%M')}*"
        
        return {
            "message": message,
            "chart_data": chart_data,
            "chart_type": "bar"
        }
    
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        traceback.print_exc()
        return {
            "message": f"Error accessing ML_Location_Risk table:\n\n{str(e)}",
            "chart_data": None,
            "chart_type": None
        }
