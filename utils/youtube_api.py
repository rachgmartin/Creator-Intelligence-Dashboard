import requests
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
                        print(f"API call failed after {max_retries} attempts: {e}")
                        return None
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure()
def search_channel_id(query, api_key):
    """Search for a YouTube channel ID by name."""
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?key={api_key}&part=id&type=channel&q={query}&maxResults=1"
    )
    response = session.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if "error" in data:
        print(f"YouTube API error: {data['error']}")
        return None
    
    try:
        return data["items"][0]["id"]["channelId"]
    except (KeyError, IndexError):
        return None

@retry_on_failure()
def get_latest_video_id(channel_id, api_key):
    """
    Fetches the most recent uploaded video ID for a given channel.
    """
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults=1"
    )
    response = session.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if "error" in data:
        print(f"YouTube API error: {data['error']}")
        return None
    
    try:
        return data['items'][0]['id']['videoId']
    except (KeyError, IndexError):
        return None

@retry_on_failure()
def get_comments(video_id, api_key, max_results=100):
    """Retrieve up to ``max_results`` top-level comments from a video."""
    comments = []
    base_url = (
        f"https://www.googleapis.com/youtube/v3/commentThreads"
        f"?key={api_key}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults=100"
    )
    page_token = ""
    
    while len(comments) < max_results:
        url = base_url + (f"&pageToken={page_token}" if page_token else "")
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                print(f"YouTube API error: {data['error']}")
                break
                
            for item in data.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
                if len(comments) >= max_results:
                    break
                    
            page_token = data.get("nextPageToken")
            if not page_token:
                break
                
        except requests.RequestException as e:
            print(f"Error fetching comments: {e}")
            break
            
    return comments


@retry_on_failure()
def get_channel_stats(channel_id, api_key):
    """Return subscriber, view, and video counts for a channel."""
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?key={api_key}&id={channel_id}&part=statistics"
    )
    response = session.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if "error" in data:
        print(f"YouTube API error: {data['error']}")
        return None
    
    try:
        stats = data["items"][0]["statistics"]
        return {
            "subscribers": format_number(stats.get("subscriberCount", "0")),
            "views": format_number(stats.get("viewCount", "0")),
            "videos": format_number(stats.get("videoCount", "0")),
        }
    except (KeyError, IndexError):
        return None


@retry_on_failure()
def get_channel_title(channel_id, api_key):
    """Fetch the public title of a channel."""
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?key={api_key}&id={channel_id}&part=snippet"
    )
    response = session.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if "error" in data:
        print(f"YouTube API error: {data['error']}")
        return None
    
    try:
        return data["items"][0]["snippet"]["title"]
    except (KeyError, IndexError):
        return None

def format_number(num_str):
    """Format large numbers with K/M/B suffixes."""
    try:
        num = int(num_str)
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
    except (ValueError, TypeError):
        return str(num_str)
