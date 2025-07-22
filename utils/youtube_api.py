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


def get_video_stats(video_id, api_key):
    """Get statistics for a specific video."""
    url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?key={api_key}&id={video_id}&part=statistics,snippet"
    )
    response = requests.get(url).json()
    try:
        item = response["items"][0]
        stats = item["statistics"]
        snippet = item["snippet"]
        return {
            "views": stats.get("viewCount"),
            "likes": stats.get("likeCount"),
            "comments": stats.get("commentCount"),
            "title": snippet.get("title"),
            "published_at": snippet.get("publishedAt"),
            "duration": snippet.get("duration")
        }
    except (KeyError, IndexError):
        return None


def get_channel_revenue_estimate(channel_id, api_key):
    """
    Estimate monthly revenue based on channel statistics and recent video performance.
    This is a rough estimate based on industry averages.
    """
    try:
        # Get channel stats
        stats = get_channel_stats(channel_id, api_key)
        if not stats:
            return None
        
        # Get recent videos for better estimation
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults=10"
        )
        response = requests.get(url).json()
        
        if not response.get("items"):
            return None
        
        total_recent_views = 0
        video_count = 0
        
        for item in response["items"]:
            video_id = item["id"]["videoId"]
            video_stats = get_video_stats(video_id, api_key)
            if video_stats and video_stats.get("views"):
                total_recent_views += int(video_stats["views"])
                video_count += 1
        
        if video_count == 0:
            return None
        
        # Calculate average views per video
        avg_views_per_video = total_recent_views / video_count
        
        # Estimate monthly uploads (assume recent 10 videos represent monthly output)
        monthly_uploads = min(video_count, 30)  # Cap at 30 videos per month
        
        # Estimate monthly views
        monthly_views = avg_views_per_video * monthly_uploads
        
        # Revenue estimation based on industry averages
        # RPM (Revenue Per Mille) typically ranges from $1-5 per 1000 views
        # We'll use a conservative estimate of $2 per 1000 views
        rpm = 2.0
        estimated_revenue = (monthly_views / 1000) * rpm
        
        # Factor in subscriber count for better estimation
        subscriber_count = int(stats["subscribers"]) if stats["subscribers"] else 0
        
        # Adjust based on subscriber count (larger channels often have higher RPM)
        if subscriber_count > 1000000:  # 1M+ subscribers
            estimated_revenue *= 1.5
        elif subscriber_count > 100000:  # 100K+ subscribers
            estimated_revenue *= 1.2
        elif subscriber_count < 10000:  # Less than 10K subscribers
            estimated_revenue *= 0.7
        
        return max(estimated_revenue, 0)  # Ensure non-negative
        
    except Exception as e:
        print(f"Error estimating revenue: {e}")
        return None


def get_recent_videos(channel_id, api_key, max_results=10):
    """Get recent videos from a channel with their stats."""
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&type=video&maxResults={max_results}"
    )
    response = requests.get(url).json()
    
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        video_stats = get_video_stats(video_id, api_key)
        if video_stats:
            videos.append({
                "video_id": video_id,
                "title": video_stats["title"],
                "views": video_stats["views"],
                "likes": video_stats["likes"],
                "comments": video_stats["comments"],
                "published_at": video_stats["published_at"]
            })
    
    return videos
