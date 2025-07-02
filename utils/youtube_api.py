import requests


def search_channel_id(query, api_key):
    """Search for a YouTube channel ID by name."""
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?key={api_key}&part=id&type=channel&q={query}&maxResults=1"
    )
    response = requests.get(url).json()
    try:
        return response["items"][0]["id"]["channelId"]
    except (KeyError, IndexError):
        return None

def get_latest_video_id(channel_id, api_key):
    """
    Fetches the most recent uploaded video ID for a given channel.
    """
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults=1"
    )
    response = requests.get(url).json()
    try:
        return response['items'][0]['id']['videoId']
    except (KeyError, IndexError):
        return None

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
        data = requests.get(url).json()
        for item in data.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
            if len(comments) >= max_results:
                break
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return comments


def get_channel_stats(channel_id, api_key):
    """Return subscriber, view, and video counts for a channel."""
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?key={api_key}&id={channel_id}&part=statistics"
    )
    data = requests.get(url).json()
    try:
        stats = data["items"][0]["statistics"]
        return {
            "subscribers": stats.get("subscriberCount"),
            "views": stats.get("viewCount"),
            "videos": stats.get("videoCount"),
        }
    except (KeyError, IndexError):
        return None


def get_channel_title(channel_id, api_key):
    """Fetch the public title of a channel."""
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?key={api_key}&id={channel_id}&part=snippet"
    )
    data = requests.get(url).json()
    try:
        return data["items"][0]["snippet"]["title"]
    except (KeyError, IndexError):
        return None
