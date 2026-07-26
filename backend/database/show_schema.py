import sqlite3

conn = sqlite3.connect("geosentinel.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

tables = cursor.fetchall()

for table in tables:
    table_name = table[0]

    print(f"\nTABLE: {table_name}")

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = cursor.fetchall()

    for column in columns:
        print(column[1])

conn.close()