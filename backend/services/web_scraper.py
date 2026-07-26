from datetime import datetime


def collect_reports(keyword):

    return {
        "source": "news",
        "keyword": keyword,
        "content": f"Collected reports related to {keyword}",
        "timestamp": str(datetime.now()),
        "status": "collected"
    }