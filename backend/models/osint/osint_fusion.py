class OSINTFusion:

    def __init__(self):
        print("OSINT Fusion Initialized")

    def summarize(self, osint_results):

        summary = {
            "google_news": {},
            "twitter": {},
            "government": {},
            "correlation": []
        }

        # -----------------------------
        # Google News
        # -----------------------------

        google = osint_results.get("google_news", {})

        articles = google.get("articles", [])

        summary["google_news"] = {

            "article_count": len(articles),

            "headlines": [

                article["title"]

                for article in articles[:5]

            ]

        }

        # -----------------------------
        # Twitter/X
        # -----------------------------

        twitter = osint_results.get("twitter", {})

        posts = twitter.get("posts", [])

        summary["twitter"] = {

            "post_count": len(posts),

            "sample_posts": [

                post.get("text", "")

                for post in posts[:5]

            ]

        }

        # -----------------------------
        # Government Sources
        # -----------------------------

        government = osint_results.get(

            "government",

            {}

        )

        summary["government"] = {

            source: len(items)

            for source, items

            in government.items()

        }

        # -----------------------------
        # Correlation
        # -----------------------------

        if len(articles) > 0:

            summary["correlation"].append(

                "Google News contains recent reports related to the detected event."

            )

        if len(posts) > 0:

            summary["correlation"].append(

                "Twitter/X users are discussing the detected event."

            )

        if any(

            len(v) > 0

            for v in government.values()

        ):

            summary["correlation"].append(

                "Official government sources also contain related reports."

            )

        if len(summary["correlation"]) == 0:

            summary["correlation"].append(

                "No external evidence was found."

            )

        return summary