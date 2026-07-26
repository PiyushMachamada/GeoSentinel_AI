from backend.database.database import get_connection


class MonitoringStateDB:
    """
    Stores the monitoring status of every AOI.
    """

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        print("Connected DB:", self.conn.execute("PRAGMA database_list").fetchall())
        print("Schema:", self.conn.execute("PRAGMA table_info(monitoring_state)").fetchall())


    def get_state(
        self,
        aoi_id,
    ):
        self.cursor.execute(
            """
            SELECT
                latest_product_id,
                analysis_date,
                checked_time,
                status
            FROM monitoring_state
            WHERE aoi_id = ?
            """,
            (aoi_id,),
        )

        row = self.cursor.fetchone()

        if row is None:
            return None

        return {
            "latest_product_id": row[0],
            "analysis_date": row[1],
            "checked_time": row[2],
            "status": row[3],
        }
    
    def update_state(
        self,
        aoi_id,
        product_id,
        analysis_date,
        checked_time,
        status="ACTIVE",
    ):
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO monitoring_state
            (
                aoi_id,
                latest_product_id,
                analysis_date,
                checked_time,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                aoi_id,
                product_id,
                analysis_date,
                checked_time,
                status,
            ),
        )

        self.conn.commit()

    def close(self):
        self.conn.close()