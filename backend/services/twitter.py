from datetime import datetime


def get_social_data(keyword):

    return {
        "platform": "Twitter/X",
        "keyword": keyword,
        "text": f"Social media information about {keyword}",
        "timestamp": str(datetime.now()),
        "status": "collected"
    }
