import requests
from urllib.parse import quote_plus
import time
from functools import wraps

# Create a session for connection pooling
session = requests.Session()

def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry API calls on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        print(f"News API call failed after {max_retries} attempts: {e}")
                        return []
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return []
        return wrapper
    return decorator

@retry_on_failure()
def fetch_news_mentions(creator_name, channel_name, api_key):
    """Fetch news mentions for a creator from GNews API."""
    if not creator_name or not api_key:
        return []
    
    # Sanitize inputs
    creator_name = creator_name.strip()
    channel_name = channel_name.strip() if channel_name else creator_name
    
    query = f'"{creator_name}" OR "{channel_name}"'
    url = f"https://gnews.io/api/v4/search?q={quote_plus(query)}&lang=en&max=10&token={api_key}"
    
    response = session.get(url, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    if "errors" in data:
        print(f"News API error: {data['errors']}")
        return []
    
    articles = data.get("articles", [])
    return [{
        "title": article.get("title", "No title"),
        "description": article.get("description", "No description"),
        "url": article.get("url", "#"),
        "source": article.get("source", {}).get("name", "Unknown source"),
        "publishedAt": article.get("publishedAt", "Unknown date")
    } for article in articles if article.get("title")]
