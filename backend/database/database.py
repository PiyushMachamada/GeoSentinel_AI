from pathlib import Path
import sqlite3

DB_NAME = Path(__file__).resolve().parent / "geosentinel.db"


def get_connection():
    print("\n==============================")
    print("Database being used:")
    print(DB_NAME.resolve())
    print("==============================\n")

    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # AOIs
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aois(

        id TEXT PRIMARY KEY,

        name TEXT NOT NULL,

        latitude REAL NOT NULL,

        longitude REAL NOT NULL,

        radius_km REAL NOT NULL,

        description TEXT,

        active INTEGER DEFAULT 1,

        monitoring_interval TEXT DEFAULT 'weekly',

        last_checked TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =====================================================
    # MONITORING STATE
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_state(

        aoi_id TEXT PRIMARY KEY,

        latest_image_id TEXT,

        latest_product_id TEXT,

        latest_acquisition_date TEXT,

        last_checked TEXT,

        last_analysis_id INTEGER,

        status TEXT,

        FOREIGN KEY (aoi_id)
            REFERENCES aois(id)
    )
    """)

    # =====================================================
    # ANALYSIS RESULTS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        analysis_name TEXT NOT NULL,

        aoi_id TEXT NOT NULL,

        aoi_name TEXT NOT NULL,

        timestamp TEXT,

        objects_detected TEXT,

        confidence_score REAL,

        change_percentage REAL,

        prithvi_results TEXT,

        grounding_dino_results TEXT,

        dynamic_world_results TEXT,

        dynamic_world_transition_results TEXT,

        evidence_results TEXT,

        historical_results TEXT,

        report TEXT,

        fusion_results TEXT,

        transition_results TEXT,

        geospatial_results TEXT,

        pipeline_version TEXT,

        execution_time REAL,

        analysis_directory TEXT,

        before_image_path TEXT,
        after_image_path TEXT,

        prithvi_before_path TEXT,
        prithvi_after_path TEXT,

        segmask_before_path TEXT,
        segmask_after_path TEXT,

        changestar_result_path TEXT,

        dynamic_world_before_path TEXT,
        dynamic_world_after_path TEXT,

        dynamic_world_transition_map TEXT,

        grounding_dino_before_path TEXT,
        grounding_dino_after_path TEXT,

        change_map_path TEXT,
        change_binary_path TEXT,

        FOREIGN KEY (aoi_id)
            REFERENCES aois(id)
    )
    """)

    # =====================================================
    # INDEXES
    # =====================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_analysis_aoi
        ON analysis_results(aoi_id)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_analysis_timestamp
        ON analysis_results(timestamp)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_analysis_aoi_timestamp
        ON analysis_results(aoi_id, timestamp)
        """)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    create_database()