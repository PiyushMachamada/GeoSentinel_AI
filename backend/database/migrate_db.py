import sqlite3

DB_NAME = "geosentinel.db"


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def migrate():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if not column_exists(cursor, "analysis_results", "analysis_name"):
        cursor.execute(
            "ALTER TABLE analysis_results ADD COLUMN analysis_name TEXT"
        )

    if not column_exists(cursor, "analysis_results", "aoi_id"):
        cursor.execute(
            "ALTER TABLE analysis_results ADD COLUMN aoi_id TEXT"
        )

    if not column_exists(cursor, "analysis_results", "aoi_name"):
        cursor.execute(
            "ALTER TABLE analysis_results ADD COLUMN aoi_name TEXT"
        )

    cursor.execute("""
        UPDATE analysis_results
        SET
            analysis_name = image_name
        WHERE
            analysis_name IS NULL
    """)

    cursor.execute("""
        UPDATE analysis_results
        SET
            aoi_id = 'AOI001'
        WHERE
            aoi_id IS NULL
    """)

    cursor.execute("""
        UPDATE analysis_results
        SET
            aoi_name = 'Kempegowda International Airport'
        WHERE
            aoi_name IS NULL
    """)

    conn.commit()
    conn.close()

    print("Database migration completed successfully.")


if __name__ == "__main__":
    migrate()