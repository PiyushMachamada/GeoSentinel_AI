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
        "aircraft. helicopter. control tower. "
        "fuel tank. cargo truck. truck. bus. vehicle. "
        "warehouse. storage building. apron. "
        "parking lot. construction site. road."
    ),

    # --------------------------------------------------
    # Port & Maritime Monitoring
    # --------------------------------------------------

    "port": (
        "ship. cargo ship. container ship. boat. "
        "container. container yard. crane. dock. quay. pier. "
        "warehouse. storage building. oil tank. "
        "truck. vehicle. road."
    ),

    # --------------------------------------------------
    # Urban Intelligence
    # --------------------------------------------------

    "urban": (
        "building. residential building. industrial building. "
        "road. bridge. construction site. parking lot. "
        "vehicle. car. truck. bus. "
        "warehouse. urban block."
    ),

    # --------------------------------------------------
    # Forest Monitoring
    # --------------------------------------------------

    "forest": (
        "tree. forest. vegetation. clearing. logging road. road. "
        "vehicle. truck. oil pipeline. "
        "building. smoke. fire."
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
        "military base. bunker. warehouse. "
        "fighter aircraft. transport aircraft. helicopter. "
        "missile launcher. radar. antenna. "
        "military vehicle. armored vehicle. truck. "
        "runway. taxiway. hangar."
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
        "building. road. bridge. airport. port. "
        "vehicle. truck. ship. crane. warehouse. "
        "industrial building. parking lot. construction site. "
        "forest. river."
    ),
}


THRESHOLDS = {

    "airport": (0.32, 0.24),

    "port": (0.30, 0.22),

    "urban": (0.34, 0.26),

    "forest": (0.24, 0.18),

    "agriculture": (0.25, 0.20),

    "mining": (0.28, 0.22),

    "industrial": (0.30, 0.24),

    "military": (0.33, 0.24),

    "construction": (0.28, 0.22),

    "road_development": (0.30, 0.22),

    "flood": (0.25, 0.18),

    "coastal": (0.28, 0.22),

    "disaster": (0.24, 0.18),

    "energy": (0.30, 0.25),

    "railway": (0.28, 0.22),

    "default": (0.35, 0.30),
}