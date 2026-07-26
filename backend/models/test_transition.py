from backend.models.transition_analysis import (
    analyze_transitions
)

print("TEST STARTED")

results = analyze_transitions()

print("RESULTS:")
print(results)

print("TOTAL TRANSITIONS:",
      len(results))

for k, v in sorted(
    results.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(
        f"{k}: {v}%"
    )

print("TEST FINISHED")