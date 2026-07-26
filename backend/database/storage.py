import json

from backend.database.database import get_connection


# ==================================
# SATELLITE DATA
# ==================================

def save_satellite_data(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO satellite_images
    (source, date, location, file_path)
    VALUES (?, ?, ?, ?)
    """, (
        data["source"],
        data["date"],
        data["region"],
        data["image"]
    ))

    conn.commit()
    conn.close()


# ==================================
# TEXT REPORTS
# ==================================

def save_text_report(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO text_reports
    (source, content, timestamp)
    VALUES (?, ?, ?)
    """, (
        data["source"],
        data["content"],
        data["timestamp"]
    ))

    conn.commit()
    conn.close()


# ==================================
# SOCIAL MEDIA POSTS
# ==================================

def save_social_post(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO social_posts
    (platform, content, timestamp)
    VALUES (?, ?, ?)
    """, (
        data["platform"],
        data["text"],
        data["timestamp"]
    ))

    conn.commit()
    conn.close()


# ==================================
# ANALYSIS HISTORY
# ==================================

def save_analysis(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO analysis_history
    (
        timestamp,
        before_image,
        after_image,
        yolo_results,
        segformer_results,
        intelligence_report,
        change_percentage
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["timestamp"],
        data["before_image"],
        data["after_image"],
        json.dumps(data["yolo_results"]),
        json.dumps(data["segformer_results"]),
        data["intelligence_report"],
        data["change_percentage"]
    ))

    conn.commit()
    conn.close()

    print("Analysis saved successfully.")

def get_latest_change_percentage():

    try:
        with open(
            "backend/outputs/change_report.txt",
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

            for line in text.split("\n"):

                if "Change Detected" in line:

                    value = (
                        line.split(":")[1]
                        .replace("%", "")
                        .strip()
                    )

                    return float(value)

    except:
        return 0.0

    return 0.0