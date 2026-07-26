import feedparser


class GoogleNewsOSINT:

    def __init__(self):

        print("Google News OSINT Initialized")

    def search(
        self,
        query,
        max_results=5
    ):

        rss_url = (
            "https://news.google.com/rss/search?q="
            + query.replace(" ", "+")
        )

        try:

            feed = feedparser.parse(rss_url)

            articles = []

            for entry in feed.entries[:max_results]:

                source = "Unknown"

                if hasattr(entry, "source"):
                    source = entry.source.title

                articles.append({

                    "title": getattr(entry, "title", ""),

                    "source": source,

                    "published": getattr(entry, "published", ""),

                    "link": getattr(entry, "link", "")

                })

            return {

                "query": query,

                "status": "success",

                "article_count": len(articles),

                "articles": articles

            }

        except Exception as e:

            print(f"Google News Error: {e}")

            return {

                "query": query,

                "status": "failed",

                "article_count": 0,

                "articles": [],

                "error": str(e)

            }