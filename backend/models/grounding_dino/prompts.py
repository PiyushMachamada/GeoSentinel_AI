"""
Grounding DINO prompts and thresholds.

GeoSentinel AI
Persistent Earth Observation Intelligence Platform
"""

PROMPTS = {

    # --------------------------------------------------
    # Civil Airport Monitoring
    # --------------------------------------------------

    "airport": (
        "runway. taxiway. terminal. hangar. "
        "aircraft. helicopter. "
        "fuel truck. vehicle. truck. bus. "
        "parking lot. warehouse. storage building. "
        "fuel tank. construction site. road."
    ),

    # --------------------------------------------------
    # Port & Maritime Monitoring
    # --------------------------------------------------

    "port": (
        "harbor. dock. pier. quay. "
        "cargo ship. container ship. boat. "
        "shipping container. container yard. "
        "crane. warehouse. storage building. "
        "truck. vehicle. fuel tank. road."
    ),

    # --------------------------------------------------
    # Urban Intelligence
    # --------------------------------------------------

    "urban": (
        "building. apartment. residential building. "
        "commercial building. road. bridge. "
        "intersection. parking lot. "
        "vehicle. car. truck. bus. motorcycle. "
        "construction site."
    ),

    # --------------------------------------------------
    # Forest Monitoring
    # --------------------------------------------------

    "forest": (
        "forest. tree. vegetation. "
        "clearing. trail. road. "
        "river. lake. "
        "building. vehicle. "
        "fire. smoke."
    ),

    # --------------------------------------------------
    # Agriculture Monitoring
    # --------------------------------------------------

    "agriculture": (
        "agricultural field. cropland. farm. "
        "greenhouse. irrigation canal. "
        "tractor. harvester. "
        "farm building. dirt road."
    ),

    # --------------------------------------------------
    # Mining Activity
    # --------------------------------------------------

    "mining": (
        "open pit mine. quarry. excavation. "
        "haul truck. excavator. bulldozer. "
        "processing plant. conveyor belt. "
        "tailings pond. road."
    ),

    # --------------------------------------------------
    # Industrial Infrastructure
    # --------------------------------------------------

    "industrial": (
        "factory. warehouse. processing plant. "
        "storage tank. smokestack. "
        "truck. railway. road."
    ),

    # --------------------------------------------------
    # Military Intelligence
    # --------------------------------------------------

    "military": (
        "military base. bunker. "
        "runway. taxiway. hangar. "
        "fighter aircraft. transport aircraft. helicopter. "
        "military vehicle. armored vehicle. truck. "
        "radar. antenna. "
        "fuel tank. warehouse."
    ),

    # --------------------------------------------------
    # Construction Monitoring
    # --------------------------------------------------

    "construction": (
        "construction site. "
        "excavator. bulldozer. crane. "
        "truck. concrete mixer. "
        "building. bridge. road."
    ),

    # --------------------------------------------------
    # Road Development
    # --------------------------------------------------

    "road_development": (
        "highway. road. bridge. "
        "intersection. overpass. "
        "construction site. "
        "truck. excavator. bulldozer."
    ),

    # --------------------------------------------------
    # Flood Monitoring
    # --------------------------------------------------

    "flood": (
        "flooded area. water. river. lake. "
        "bridge. road. "
        "building. house. "
        "vehicle. boat."
    ),

    # --------------------------------------------------
    # Coastal Monitoring
    # --------------------------------------------------

    "coastal": (
        "shoreline. beach. harbor. dock. "
        "boat. ship. pier. "
        "road. bridge. building."
    ),

    # --------------------------------------------------
    # Disaster Monitoring
    # --------------------------------------------------

    "disaster": (
        "collapsed building. damaged building. "
        "fire. smoke. flood. "
        "road. bridge. "
        "vehicle. rescue vehicle."
    ),

    # --------------------------------------------------
    # Energy Infrastructure
    # --------------------------------------------------

    "energy": (
        "power plant. substation. "
        "solar panel. wind turbine. "
        "oil tank. gas tank. "
        "pipeline. transmission tower."
    ),

    # --------------------------------------------------
    # Railway Monitoring
    # --------------------------------------------------

    "railway": (
        "railway. train. locomotive. "
        "rail yard. station. "
        "bridge. road. "
        "warehouse."
    ),

    # --------------------------------------------------
    # Generic EO Monitoring
    # --------------------------------------------------

    "default": (
        "building. road. bridge. "
        "vehicle. truck. "
        "warehouse. parking lot. "
        "construction site. "
        "river. forest."
    ),
}


THRESHOLDS = {

    "airport": (0.30, 0.25),

    "port": (0.28, 0.22),

    "urban": (0.32, 0.25),

    "forest": (0.22, 0.18),

    "agriculture": (0.25, 0.20),

    "mining": (0.28, 0.22),

    "industrial": (0.30, 0.24),

    "military": (0.30, 0.25),

    "construction": (0.28, 0.22),

    "road_development": (0.30, 0.22),

    "flood": (0.25, 0.18),

    "coastal": (0.28, 0.22),

    "disaster": (0.24, 0.18),

    "energy": (0.30, 0.25),

    "railway": (0.28, 0.22),

    "default": (0.35, 0.30),
}