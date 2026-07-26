import statistics

from backend.database.database import get_connection


class TemporalEngine:
    """
    Persistent AOI Intelligence Engine

    Responsibilities
    ----------------
    - Read historical analyses
    - Compute temporal trends
    - Calculate stability
    - Calculate growth
    - Provide dashboard timeline data
    """

    def __init__(self):

        print("Temporal Intelligence Engine Initialized")

    # ==========================================
    # Load Mission History
    # ==========================================

    def get_history(self, aoi_id):

        conn = get_connection()

        conn.row_factory = __import__("sqlite3").Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM analysis_results
            WHERE aoi_id = ?
            ORDER BY timestamp ASC
            """,
            (aoi_id,),
        )

        rows = cursor.fetchall()

        conn.close()

        return [dict(r) for r in rows]
    
        # ==========================================
    # Change Trend
    # ==========================================

    def analyze_change_trend(
        self,
        history,
    ):

        if len(history) < 2:

            return {

                "trend": "Insufficient Data",

                "average_change": 0,

                "history": []

            }

        changes = [

            h["change_percentage"]

            for h in history

        ]

        average_change = round(

            statistics.mean(changes),

            2

        )

        trend = "Stable"

        if changes[-1] > changes[0]:

            trend = "Increasing"

        elif changes[-1] < changes[0]:

            trend = "Decreasing"

        return {

            "trend": trend,

            "average_change": average_change,

            "history": changes,

        }
    
        # ==========================================
    # Stability
    # ==========================================

    def stability_score(
        self,
        history,
    ):

        if not history:

            return 0

        changes = [

            h["change_percentage"]

            for h in history

        ]

        avg_change = statistics.mean(changes)

        stability = max(

            0,

            100 - avg_change

        )

        return round(

            stability,

            2

        )
    
        # ==========================================
    # Growth
    # ==========================================

    def growth_rate(
        self,
        history,
    ):

        if len(history) < 2:

            return 0

        first = history[0]["change_percentage"]

        last = history[-1]["change_percentage"]

        years = max(

            1,

            len(history) - 1

        )

        growth = (

            last - first

        ) / years

        return round(

            growth,

            2

        )
    
        # ==========================================
    # Full Temporal Intelligence
    # ==========================================

    def analyze(
        self,
        aoi_id,
    ):

        history = self.get_history(aoi_id)

        return {

            "missions": len(history),

            "trend": self.analyze_change_trend(history),

            "stability": self.stability_score(history),

            "growth_rate": self.growth_rate(history),

            "history": history,

        }