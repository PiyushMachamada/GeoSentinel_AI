from backend.models.dynamic_world_temporal_analysis import (
    compare_dynamic_world
)

results = compare_dynamic_world()

print(
    "\nDynamic World Temporal Analysis"
)

for cls, data in results.items():

    print(
        f"{cls}: "
        f"{data['before']}% -> "
        f"{data['after']}% "
        f"({data['change']}%)"
    )