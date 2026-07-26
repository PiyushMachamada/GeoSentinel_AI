import sqlite3

from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / "geosentinel.db"


def get_latest_analysis(aoi_id):

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM analysis_results
        WHERE aoi_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (aoi_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)

def get_analysis_by_id(analysis_id):

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM analysis_results
        WHERE id = ?
        LIMIT 1
        """,
        (analysis_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)

def get_analysis_history(aoi_id):

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM analysis_results
        WHERE aoi_id = ?
        ORDER BY timestamp DESC
        """,
        (aoi_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

def get_analysis_timeline(aoi_id):

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            analysis_name,
            aoi_id,
            aoi_name,
            timestamp,
            change_percentage,
            confidence_score
        FROM analysis_results
        WHERE aoi_id = ?
        ORDER BY timestamp DESC
        """,
        (aoi_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]