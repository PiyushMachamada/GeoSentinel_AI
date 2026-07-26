from dataclasses import dataclass
import ee


@dataclass
class AOI:
    """
    Area of Interest definition used throughout GeoSentinel AI.
    """

    id: str
    name: str

    latitude: float
    longitude: float
    radius_km: float

    # ==========================================
    # Mission Type
    # ==========================================

    mission_type: str = "urban"

    # ==========================================
    # Temporal Monitoring
    # ==========================================

    before_start: str = ""
    before_end: str = ""

    after_start: str = ""
    after_end: str = ""

    active: bool = True
    description: str = ""

    # ==========================================
    # Earth Engine ROI
    # ==========================================

    def to_ee_geometry(self):
        """
        Converts the AOI into an Earth Engine rectangle.
        """

        delta = self.radius_km / 111.32

        return ee.Geometry.Rectangle([
            self.longitude - delta,
            self.latitude - delta,
            self.longitude + delta,
            self.latitude + delta,
        ])


class AOIManager:
    """
    Manages all Areas of Interest (AOIs).
    """

    def __init__(self):

        self._aois = [

            AOI(

                id="AOI001",

                name="Kempegowda International Airport",

                latitude=13.1986,
                longitude=77.7066,
                radius_km=5,

                mission_type="airport",

                before_start="2020-01-01",
                before_end="2020-12-31",

                after_start="2024-01-01",
                after_end="2024-12-31",

                description="Airport Monitoring",

            ),

            AOI(

                id="AOI002",

                name="Jawaharlal Nehru Port (JNPT)",

                latitude=18.9497,
                longitude=72.9523,
                radius_km=8,

                mission_type="port",

                before_start="2020-01-01",
                before_end="2020-12-31",

                after_start="2024-01-01",
                after_end="2024-12-31",

                description="Port Monitoring",

            ),

            AOI(

                id="AOI003",

                name="Strait of Hormuz",

                latitude=26.5667,
                longitude=56.2500,
                radius_km=25,

                mission_type="military",

                before_start="2020-01-01",
                before_end="2020-12-31",

                after_start="2024-01-01",
                after_end="2024-12-31",

                description="Maritime Security Monitoring",

            ),

            AOI(

                id="AOI004",

                name="Amazon Rainforest",

                latitude=-3.4653,
                longitude=-62.2159,
                radius_km=25,

                mission_type="forest",

                before_start="2020-01-01",
                before_end="2020-12-31",

                after_start="2024-01-01",
                after_end="2024-12-31",

                description="Deforestation Monitoring",

            ),

            AOI(

                id="AOI005",

                name="Bengaluru Urban Expansion",

                latitude=12.9716,
                longitude=77.5946,
                radius_km=15,

                mission_type="urban",

                before_start="2020-01-01",
                before_end="2020-12-31",

                after_start="2024-01-01",
                after_end="2024-12-31",

                description="Urban Growth Monitoring",

            ),

        ]

    def get_all(self):
        return self._aois

    def get_active(self):
        return [
            aoi
            for aoi in self._aois
            if aoi.active
        ]

    def get_by_id(self, aoi_id):

        for aoi in self._aois:

            if aoi.id == aoi_id:
                return aoi

        return None