from datetime import datetime


def generate_report(change_percentage):

    report = f"""
GeoSentinel Analysis Report
===========================

Generated:
{datetime.now()}

Modules Executed:
-----------------
✓ YOLO Object Detection
✓ SegFormer Scene Understanding
✓ Change Detection

Change Analysis:
----------------
Change Detected: {change_percentage:.2f} %

Output Files:
-------------
backend/outputs/yolo_result.jpg
backend/outputs/segformer_result.png
backend/outputs/change_map.jpg

GeoSentinel Pipeline Status:
----------------------------
SUCCESS
"""

    with open(
        "demo_results/report.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(report)

    print("Report generated!")