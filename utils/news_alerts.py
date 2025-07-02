import requests
from urllib.parse import quote_plus

def fetch_news_mentions(creator_name, channel_name, api_key):
    query = f'"{creator_name}" OR "{channel_name}"'
    url = f"https://gnews.io/api/v4/search?q={quote_plus(query)}&lang=en&max=10&token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [{
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "source": article["source"]["name"],
            "publishedAt": article["publishedAt"]
        } for article in articles]
    else:
        return []
