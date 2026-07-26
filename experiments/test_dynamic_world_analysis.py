from backend.models.dynamic_world_analysis import analyze_dynamic_world


results = analyze_dynamic_world(
    "dynamic_world.tif"
)

print("\nDynamic World Analysis\n")

for k, v in results.items():
    print(f"{k}: {v}%")