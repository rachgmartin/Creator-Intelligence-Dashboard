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
        f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
    )
    response = requests.get(url).json()
    try:
        return response['items'][0]['id']['videoId']
    except (KeyError, IndexError):
        return None

def get_comments(video_id, api_key, max_results=100):
    """
    Retrieves top-level comments from a video.
    """
    comments = []
    url = (
        f"https://www.googleapis.com/youtube/v3/commentThreads"
        f"?key={api_key}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults={max_results}"
    )
    response = requests.get(url).json()
    try:
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
    except Exception:
        pass
    return comments
