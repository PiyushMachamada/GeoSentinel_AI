from fastapi import APIRouter, HTTPException
from backend.database.database import get_connection

router = APIRouter(
    prefix="/aois",
    tags=["AOIs"]
)


@router.get("/")
def get_aois():

    conn = get_connection()
    conn.row_factory = None

    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(aois)")
    columns = {row[1] for row in cursor.fetchall()}

    if "aoi_id" in columns:
        id_column = "aoi_id"
    elif "id" in columns:
        id_column = "id"
    else:
        conn.close()
        raise HTTPException(
            status_code=500,
            detail="AOI table is missing id columns.",
        )

    mission_column = (
        "mission_type"
        if "mission_type" in columns
        else "NULL AS mission_type"
    )

    cursor.execute(f"""
        SELECT

            {id_column} AS aoi_id,
            name,
            latitude,
            longitude,
            radius_km,
            {mission_column},
            description,
            active,
            monitoring_interval,
            last_checked,
            created_at

        FROM aois

        ORDER BY name
    """)

    rows = cursor.fetchall()

    conn.close()

    aois = []

    for row in rows:

        aois.append({

            "id": row[0],
            "name": row[1],
            "latitude": row[2],
            "longitude": row[3],
            "radius_km": row[4],
            "mission_type": row[5],
            "description": row[6],
            "active": bool(row[7]),
            "monitoring_interval": row[8],
            "last_checked": row[9],
            "created_at": row[10],

        })

    return aois