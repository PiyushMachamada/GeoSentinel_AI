"""
Loads the knowledge base for a given AOI profile.
"""

from intelligence.knowledge.airport import AIRPORT_EVENTS
from intelligence.knowledge.military import MILITARY_EVENTS
from intelligence.knowledge.forest import FOREST_EVENTS


KNOWLEDGE = {

    "Airport": AIRPORT_EVENTS,

    "Military": MILITARY_EVENTS,

    "Forest": FOREST_EVENTS,

}


def load(profile_name):

    return KNOWLEDGE.get(profile_name, {})