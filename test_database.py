import sqlite3

conn = sqlite3.connect(
    "geosentinel.db"
)

cursor = conn.cursor()

cursor.execute(
    "SELECT * FROM analysis_history"
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()