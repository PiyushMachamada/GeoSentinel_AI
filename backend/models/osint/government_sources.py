import feedparser


class GovernmentOSINT:

    def __init__(self):

        print("Government OSINT Initialized")

        self.sources = {

            "NASA Earth Observatory":
                "https://earthobservatory.nasa.gov/feeds/image-of-the-day.rss",

            "ReliefWeb":
                "https://reliefweb.int/updates/rss.xml",

            "USGS":
                "https://www.usgs.gov/news/all/feed"

        }

    def collect(self, max_results=3):

        results = {}

        for source, url in self.sources.items():

            try:

                feed = feedparser.parse(url)

                articles = []

                for entry in feed.entries[:max_results]:

                    articles.append({

                        "title": getattr(entry, "title", ""),

                        "published": getattr(
                            entry,
                            "published",
                            "Unknown"
                        ),

                        "link": getattr(entry, "link", "")

                    })

                results[source] = {

                    "status": "success",

                    "article_count": len(articles),

                    "articles": articles

                }

            except Exception as e:

                print(f"{source} Error: {e}")

                results[source] = {

                    "status": "failed",

                    "article_count": 0,

                    "articles": [],

                    "error": str(e)

                }

        return results