from pprint import pprint

from backend.models.osint.osint_engine import (
    OSINTEngine
)

engine = OSINTEngine()

results = engine.collect(
    "Flood Bangalore"
)

pprint(results)