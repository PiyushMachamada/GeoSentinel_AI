import json

from backend.models.opencd.opencd_model import OpenCDModel

import sys

BEFORE = sys.argv[1]
AFTER = sys.argv[2]

print("Loading OpenCD...")

model = OpenCDModel()

print("Running OpenCD...")

result = model.predict(BEFORE, AFTER)

with open(
    "backend/outputs/opencd_result.json",
    "w"
) as f:
    json.dump(result, f)

print("Finished.")