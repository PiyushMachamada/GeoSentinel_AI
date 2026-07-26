"""
profiles.py

GeoSentinel AI - Intelligence Profiles

This module defines Area of Interest (AOI) intelligence profiles.

Each profile describes the types of activities that are expected within
a particular environment and the evidence that should be considered
important during intelligence reasoning.

The Rule Engine uses these profiles to determine which rules should be
applied for a given AOI.

Supported profiles include:

- Airport
- Port
- Urban
- Forest
- Agriculture
- Military
- Industrial
- Mining

Additional profiles can easily be added without modifying the reasoning
engine.
"""

from dataclasses import dataclass, field


# ==========================================================
# AOI Profile
# ==========================================================

@dataclass
class AOIProfile:
    """
    Defines how an AOI should be analysed.
    """

    name: str

    description: str

    important_objects: list[str] = field(default_factory=list)

    important_landcover: list[str] = field(default_factory=list)

    important_events: list[str] = field(default_factory=list)


# ==========================================================
# Built-in Profiles
# ==========================================================

AIRPORT = AOIProfile(

    name="Airport",

    description="Airport monitoring and infrastructure analysis.",

    important_objects=[
        "airplane",
        "helicopter",
        "terminal",
        "hangar",
        "fuel tank",
        "truck",
        "construction vehicle",
    ],

    important_landcover=[
        "built",
        "bare",
        "road",
    ],

    important_events=[
        "Airport Expansion",
        "Runway Construction",
        "Aircraft Activity",
    ],
)

PORT = AOIProfile(

    name="Port",

    description="Port and maritime infrastructure monitoring.",

    important_objects=[
        "ship",
        "container",
        "crane",
        "truck",
        "warehouse",
    ],

    important_landcover=[
        "water",
        "built",
    ],

    important_events=[
        "Port Expansion",
        "Container Activity",
        "Ship Movement",
    ],
)

URBAN = AOIProfile(

    name="Urban",

    description="Urban development monitoring.",

    important_objects=[
        "building",
        "car",
        "bus",
        "truck",
    ],

    important_landcover=[
        "built",
        "road",
    ],

    important_events=[
        "Urban Expansion",
        "Construction Activity",
    ],
)

FOREST = AOIProfile(

    name="Forest",

    description="Forest and vegetation monitoring.",

    important_objects=[],

    important_landcover=[
        "trees",
        "grass",
        "shrub_and_scrub",
    ],

    important_events=[
        "Deforestation",
        "Vegetation Loss",
        "Wildfire Damage",
    ],
)

AGRICULTURE = AOIProfile(

    name="Agriculture",

    description="Agricultural monitoring.",

    important_objects=[
        "tractor",
    ],

    important_landcover=[
        "crops",
        "grass",
    ],

    important_events=[
        "Crop Expansion",
        "Crop Loss",
    ],
)

MILITARY = AOIProfile(

    name="Military",

    description="Military installation monitoring.",

    important_objects=[
        "airplane",
        "helicopter",
        "truck",
        "tank",
        "building",
    ],

    important_landcover=[
        "built",
        "bare",
    ],

    important_events=[
        "Military Activity",
        "Infrastructure Expansion",
    ],
)

INDUSTRIAL = AOIProfile(

    name="Industrial",

    description="Industrial facility monitoring.",

    important_objects=[
        "warehouse",
        "truck",
        "crane",
    ],

    important_landcover=[
        "built",
    ],

    important_events=[
        "Industrial Expansion",
    ],
)

MINING = AOIProfile(

    name="Mining",

    description="Mining activity monitoring.",

    important_objects=[
        "excavator",
        "truck",
    ],

    important_landcover=[
        "bare",
    ],

    important_events=[
        "Mining Expansion",
    ],
)


# ==========================================================
# Registry
# ==========================================================

PROFILE_REGISTRY = {

    "airport": AIRPORT,

    "port": PORT,

    "urban": URBAN,

    "forest": FOREST,

    "agriculture": AGRICULTURE,

    "military": MILITARY,

    "industrial": INDUSTRIAL,

    "mining": MINING,

}


# ==========================================================
# Helper Functions
# ==========================================================

def get_profile(profile_name: str) -> AOIProfile:
    """
    Return an AOI profile by name.

    Raises
    ------
    ValueError
        If the requested profile does not exist.
    """

    profile = PROFILE_REGISTRY.get(profile_name.lower())

    if profile is None:

        raise ValueError(
            f"Unknown AOI profile: {profile_name}"
        )

    return profile


def list_profiles() -> list[str]:
    """
    Return all available profile names.
    """

    return sorted(PROFILE_REGISTRY.keys())