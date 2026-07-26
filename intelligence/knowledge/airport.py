"""
Knowledge base for airport monitoring.
"""

AIRPORT_EVENTS = {

    "Airport Expansion": {

        "required_objects": [
            "building",
            "construction vehicle",
            "truck",
            "crane"
        ],

        "minimum_change": 15,

        "landcover": [
            "built",
            "bare"
        ],

        "priority": "High"

    },

    "Aircraft Activity": {

        "required_objects": [
            "airplane",
            "helicopter"
        ],

        "priority": "Medium"

    },

    "Fuel Infrastructure": {

        "required_objects": [
            "fuel tank"
        ],

        "priority": "High"

    }

}