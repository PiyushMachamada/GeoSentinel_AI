from googlesearch import search


class TwitterOSINT:

    def __init__(self):

        print("Twitter/X OSINT Initialized")

    def search(self, query, limit=5):

        results = []

        try:

            search_query = f"site:x.com {query}"

            for url in search(
                search_query,
                num_results=limit
            ):

                results.append({

                    "title": "Twitter/X Post",

                    "link": url

                })

            return {

                "query": query,

                "status": "success",

                "post_count": len(results),

                "posts": results

            }

        except Exception as e:

            print(f"Twitter/X Error: {e}")

            return {

                "query": query,

                "status": "failed",

                "post_count": 0,

                "posts": [],

                "error": str(e)

            }