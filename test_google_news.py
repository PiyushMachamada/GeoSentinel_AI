from backend.models.osint.google_news import GoogleNewsOSINT

news = GoogleNewsOSINT()

results = news.search("Flood Bangalore")

for article in results:
    print(article)