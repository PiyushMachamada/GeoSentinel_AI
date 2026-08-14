from backend.database.database import get_connection


class MonitoringStateDB:
    """
    Stores the monitoring status of every AOI.
    """

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        schema_rows = self.conn.execute(
            "PRAGMA table_info(monitoring_state)"
        ).fetchall()
        self.columns = {row[1] for row in schema_rows}

        self.product_column = (
            "latest_product_id"
            if "latest_product_id" in self.columns
            else "latest_image_id"
        )

        self.analysis_date_column = (
            "analysis_date"
            if "analysis_date" in self.columns
            else "latest_acquisition_date"
        )

        self.checked_time_column = (
            "checked_time"
            if "checked_time" in self.columns
            else "last_checked"
        )

        if "aoi_id" not in self.columns:
            raise RuntimeError(
                "monitoring_state table is missing required column: aoi_id"
            )


    def get_state(
        self,
        aoi_id,
    ):
        self.cursor.execute(
            f"""
            SELECT
                {self.product_column} AS latest_product_id,
                {self.analysis_date_column} AS analysis_date,
                {self.checked_time_column} AS checked_time,
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
        upsert_columns = ["aoi_id"]
        upsert_values = [aoi_id]

        if self.product_column in self.columns:
            upsert_columns.append(self.product_column)
            upsert_values.append(product_id)
        if self.analysis_date_column in self.columns:
            upsert_columns.append(self.analysis_date_column)
            upsert_values.append(analysis_date)
        if self.checked_time_column in self.columns:
            upsert_columns.append(self.checked_time_column)
            upsert_values.append(checked_time)
        if "status" in self.columns:
            upsert_columns.append("status")
            upsert_values.append(status)

        if len(upsert_columns) <= 1:
            raise RuntimeError(
                "monitoring_state table has no writable state columns."
            )

        placeholders = ", ".join(["?"] * len(upsert_columns))
        column_sql = ", ".join(
            f'"{column}"'
            for column in upsert_columns
        )

        self.cursor.execute(
            f"""
            INSERT OR REPLACE INTO monitoring_state ({column_sql})
            VALUES ({placeholders})
            """,
            tuple(upsert_values),
        )

        self.conn.commit()

    def close(self):
        self.conn.close()