from backend.models.osint.google_news import GoogleNewsOSINT
from backend.models.osint.government_sources import GovernmentOSINT
from backend.models.osint.query_builder import OSINTQueryBuilder
from backend.models.osint.twitter_osint import TwitterOSINT


class OSINTEngine:

    def __init__(self):

        print("\nLoading OSINT Engine...")

        self.google = GoogleNewsOSINT()

        self.government = GovernmentOSINT()
        
        self.query_builder = OSINTQueryBuilder()
        
        self.twitter = TwitterOSINT()

    def collect(
        self,
        prithvi_results,
        dynamic_world_results,
        transition_results,
        geospatial_results
    ):

        query = self.query_builder.build(

            prithvi_results,

            dynamic_world_results,

            transition_results,

            geospatial_results

        )

        print(f"\nOSINT Query : {query}")

        google_results = []
        twitter_results = []
        government_results = []

        try:
            google_results = self.google.search(query)
        except Exception as e:
            print(f"Google News Error: {e}")

        try:
            twitter_results = self.twitter.search(query)
        except Exception as e:
            print(f"Twitter Error: {e}")

        try:
            government_results = self.government.collect()
        except Exception as e:
            print(f"Government Source Error: {e}")

        return {

            "query": query,

            "google_news": google_results,

            "twitter": twitter_results,

            "government": government_results

        }