#!/usr/bin/env python3
"""Database schema checker"""
import pyodbc

conn_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=20.3.236.169,1433;DATABASE=CHECK_ELM_AlUlaRC_DW;UID=sa;PWD=StrongPass123!;'
conn = pyodbc.connect(conn_string)
c = conn.cursor()

print("=== EVENTS BY YEAR ===")
c.execute('SELECT YEAR(SubmitionDate) as yr, COUNT(*) as cnt FROM Event WHERE IsDeleted = 0 GROUP BY YEAR(SubmitionDate) ORDER BY yr')
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]} events")

print("\n=== TOTAL COUNTS ===")
c.execute('SELECT COUNT(*) FROM Event WHERE IsDeleted = 0')
print(f"  Total Events: {c.fetchone()[0]}")

c.execute('SELECT COUNT(*) FROM EventViolation')
print(f"  Total Violations: {c.fetchone()[0]}")

c.execute('SELECT COUNT(*) FROM Locations WHERE Isdeleted = 0')
print(f"  Total Locations: {c.fetchone()[0]}")

print("\n=== EVENT STATUS DISTRIBUTION ===")
c.execute('SELECT Status, COUNT(*) as cnt FROM Event WHERE IsDeleted = 0 GROUP BY Status ORDER BY cnt DESC')
for row in c.fetchall():
    print(f"  Status {row[0]}: {row[1]}")

print("\n=== VIOLATIONS BY SEVERITY ===")
c.execute('SELECT Severity, COUNT(*) as cnt FROM EventViolation GROUP BY Severity ORDER BY Severity')
for row in c.fetchall():
    print(f"  Severity {row[0]}: {row[1]}")

print("\n=== MONTHLY TREND (Last 12 months) ===")
c.execute('''
SELECT YEAR(SubmitionDate) as yr, MONTH(SubmitionDate) as mo, COUNT(*) as cnt 
FROM Event WHERE IsDeleted = 0 
GROUP BY YEAR(SubmitionDate), MONTH(SubmitionDate)
ORDER BY yr DESC, mo DESC
''')
for row in c.fetchall()[:12]:
    print(f"  {row[0]}-{row[1]:02d}: {row[2]} events")

c.close()
conn.close()
