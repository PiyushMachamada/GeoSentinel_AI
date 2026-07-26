import sqlite3

conn = sqlite3.connect("geosentinel.db")
cursor = conn.cursor()

print("\nTABLES")
print("=" * 40)

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

for table in cursor.fetchall():
    print(table)

print("\nROWS")
print("=" * 40)

try:
    cursor.execute(
        "SELECT * FROM analysis_results"
    )

    rows = cursor.fetchall()

    print(f"Total rows: {len(rows)}\n")

    for row in rows:
        print(row)

except Exception as e:
    print("ERROR:", e)

conn.close()