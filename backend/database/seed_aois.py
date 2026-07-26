from backend.database.database import get_connection

AOIS = [
    (
        "AOI001",
        "Kempegowda International Airport",
        13.1986,
        77.7066,
        10,
        "International Airport",
        1,
        "6 Hours",
    ),
    (
        "AOI002",
        "Jawaharlal Nehru Port (JNPT)",
        18.9490,
        72.9520,
        10,
        "Major Seaport",
        1,
        "12 Hours",
    ),
    (
        "AOI003",
        "Strait of Hormuz",
        26.5660,
        56.2500,
        25,
        "Strategic Maritime Chokepoint",
        1,
        "Daily",
    ),
    (
        "AOI004",
        "Amazon Rainforest",
        -3.4653,
        -62.2159,
        50,
        "Deforestation Monitoring",
        1,
        "Weekly",
    ),
    (
        "AOI005",
        "Bengaluru Urban Expansion",
        12.9716,
        77.5946,
        20,
        "Urban Growth Monitoring",
        1,
        "Daily",
    ),
]

conn = get_connection()
cursor = conn.cursor()

cursor.executemany(
    """
    INSERT OR IGNORE INTO aois (
        id,
        name,
        latitude,
        longitude,
        radius_km,
        description,
        active,
        monitoring_interval
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    AOIS,
)

conn.commit()
conn.close()

print("AOIs seeded successfully.")