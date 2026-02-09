#!/usr/bin/env python3
"""Test script to verify all major query categories"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v2/chat"

test_queries = [
    ("How many total inspections?", "reports_total_count"),
    ("How many violations in 2024?", "violations_total_count"),
    ("Top inspectors by count", "inspectors_by_count"),
    ("Monthly trend of inspections", "reports_monthly_trend"),
    ("Violation trend analysis", "violations_monthly_trend"),
    ("Locations by violations", "locations_by_violations"),
    ("Year over year comparison", "complex_year_comparison"),
]

print("Testing SQL Template Mapping")
print("="*60)

for query, expected in test_queries:
    try:
        resp = requests.post(BASE_URL, 
            json={'message': query, 'language': 'en'},
            timeout=90)
        
        if resp.status_code == 200:
            data = resp.json()
            template = data.get('template_id', 'N/A')
            result = data.get('data', [])
            match = "✅" if expected in template else "⚠️"
            print(f"{match} Query: {query[:40]}")
            print(f"   Template: {template}")
            print(f"   Data: {str(result)[:100]}...")
            print()
        else:
            print(f"❌ Query failed: {query[:40]} - Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {query[:40]} - {e}")
    
    time.sleep(1)  # Rate limit

print("\nDone!")
