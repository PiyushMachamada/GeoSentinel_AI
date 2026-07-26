from backend.models.qwen_reasoning import (
    generate_qwen_report
)

report = generate_qwen_report(
    {"forest": -47.53},
    {"change_percentage": 18.27},
    {"forest": 98.42},
    {"forest_to_river": 73.97},
    {"resolution": "300m"},
    {"water": 99.99}
)

print(report)