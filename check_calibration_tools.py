import sqlite3
import os
from datetime import datetime, timedelta

# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), 'database', 'tools.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if there are any tools that require calibration
cursor.execute("SELECT COUNT(*) FROM tools WHERE requires_calibration = 1")
count = cursor.fetchone()[0]
print(f"Tools requiring calibration: {count}")

# Get details of tools requiring calibration
if count > 0:
    cursor.execute("SELECT id, tool_number, next_calibration_date FROM tools WHERE requires_calibration = 1")
    tools = cursor.fetchall()
    for tool in tools:
        print(f"Tool ID: {tool[0]}, Tool Number: {tool[1]}, Next Calibration Date: {tool[2]}")

# Check if there are any tools due for calibration in the next 30 days
now = datetime.utcnow()
threshold_date = now + timedelta(days=30)
now_str = now.strftime('%Y-%m-%d %H:%M:%S')
threshold_str = threshold_date.strftime('%Y-%m-%d %H:%M:%S')

cursor.execute("""
    SELECT COUNT(*) FROM tools 
    WHERE requires_calibration = 1 
    AND next_calibration_date IS NOT NULL 
    AND next_calibration_date <= ? 
    AND next_calibration_date >= ?
""", (threshold_str, now_str))
count = cursor.fetchone()[0]
print(f"\nTools due for calibration in the next 30 days: {count}")

# Get details of tools due for calibration
if count > 0:
    cursor.execute("""
        SELECT id, tool_number, next_calibration_date FROM tools 
        WHERE requires_calibration = 1 
        AND next_calibration_date IS NOT NULL 
        AND next_calibration_date <= ? 
        AND next_calibration_date >= ?
    """, (threshold_str, now_str))
    tools = cursor.fetchall()
    for tool in tools:
        print(f"Tool ID: {tool[0]}, Tool Number: {tool[1]}, Next Calibration Date: {tool[2]}")

# Check if there are any calibration records
cursor.execute("SELECT COUNT(*) FROM tool_calibrations")
count = cursor.fetchone()[0]
print(f"\nCalibration records: {count}")

# Get details of calibration records
if count > 0:
    cursor.execute("SELECT id, tool_id, calibration_date FROM tool_calibrations")
    records = cursor.fetchall()
    for record in records:
        print(f"Calibration ID: {record[0]}, Tool ID: {record[1]}, Date: {record[2]}")

# Close the connection
conn.close()
