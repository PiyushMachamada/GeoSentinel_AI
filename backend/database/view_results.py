import sqlite3

conn = sqlite3.connect("geosentinel.db")

cursor = conn.cursor()

cursor.execute(
    "SELECT id, timestamp, confidence_score, change_percentage FROM analysis_results"
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()