from backend.database.database import get_connection


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==========================================================
    # AOIs
    # ==========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aois (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        aoi_id TEXT UNIQUE NOT NULL,

        name TEXT NOT NULL,

        latitude REAL NOT NULL,
        longitude REAL NOT NULL,

        radius_km REAL NOT NULL,

        mission_type TEXT,

        description TEXT,

        active INTEGER DEFAULT 1,

        monitoring_interval TEXT DEFAULT 'Daily',

        last_checked TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cursor.executemany("""
    INSERT OR IGNORE INTO aois (

        aoi_id,
        name,
        latitude,
        longitude,
        radius_km,
        mission_type,
        description,
        active,
        monitoring_interval

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [

    (
        "AOI001",
        "Kempegowda International Airport",
        13.1986,
        77.7066,
        5,
        "airport",
        "Airport Monitoring",
        1,
        "6 Hours"
    ),

    (
        "AOI002",
        "Jawaharlal Nehru Port (JNPT)",
        18.9497,
        72.9523,
        8,
        "port",
        "Port Monitoring",
        1,
        "12 Hours"
    ),

    (
        "AOI003",
        "Strait of Hormuz",
        26.5667,
        56.2500,
        25,
        "military",
        "Maritime Security Monitoring",
        1,
        "Daily"
    ),

    (
        "AOI004",
        "Amazon Rainforest",
        -3.4653,
        -62.2159,
        25,
        "forest",
        "Deforestation Monitoring",
        1,
        "Weekly"
    ),

    (
        "AOI005",
        "Bengaluru Urban Expansion",
        12.9716,
        77.5946,
        15,
        "urban",
        "Urban Growth Monitoring",
        1,
        "Daily"
    ),

    ])

    # ==========================================================
    # Monitoring State
    # ==========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_state (

        aoi_id TEXT PRIMARY KEY,

        latest_product_id TEXT,

        analysis_date TEXT,

        checked_time TEXT,

        status TEXT
    )
    """)

    # ==========================================================
    # Satellite Images
    # ==========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS satellite_images (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        aoi_id TEXT,

        source TEXT,

        acquisition_date TEXT,

        file_path TEXT,

        cloud_cover REAL,

        created_at TEXT
    )
    """)

    # ==========================================================
    # OSINT Reports
    # ==========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS text_reports (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        aoi_id TEXT,

        source TEXT,

        title TEXT,

        content TEXT,

        url TEXT,

        timestamp TEXT
    )
    """)

    # ==========================================================
    # Social Media
    # ==========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_posts (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        aoi_id TEXT,

        platform TEXT,

        author TEXT,

        content TEXT,

        url TEXT,

        timestamp TEXT
    )
    """)

    # ==========================================================
    # Main Analysis Table
    # ==========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            analysis_name TEXT,

            timestamp TEXT,

            aoi_id TEXT NOT NULL,
            aoi_name TEXT,

            image_name TEXT,

            confidence_score REAL,
            change_percentage REAL,

            objects_detected TEXT,

            prithvi_results TEXT,

            dynamic_world_results TEXT,
            dynamic_world_transition_results TEXT,

            fusion_results TEXT,
            transition_results TEXT,

            geospatial_results TEXT,

            evidence_results TEXT,

            report TEXT,

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

            change_map_path TEXT,
            change_binary_path TEXT,

            dynamic_world_before_path TEXT,
            dynamic_world_after_path TEXT,

            dynamic_world_transition_map TEXT,

            grounding_dino_before_path TEXT,
            grounding_dino_after_path TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("\nGeoSentinel database initialized successfully.")


if __name__ == "__main__":
    create_tables()