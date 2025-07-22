from textblob import TextBlob
from collections import Counter
import re

def clean_comment(text):
    """Clean and normalize comment text."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove very short comments (likely spam or noise)
    if len(text) < 3:
        return ""
    
    return text

def analyze_sentiment(text):
    """Analyze sentiment of a comment with improved thresholds."""
    cleaned_text = clean_comment(text)
    if not cleaned_text:
        return "neutral"
    
    try:
        blob = TextBlob(cleaned_text)
        polarity = blob.sentiment.polarity
        
        # Adjusted thresholds for better classification
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    except Exception as e:
        print(f"Error analyzing sentiment for text: {e}")
        return "neutral"

def sentiment_summary(comments):
    """Return sentiment percentages and example comments."""
    if not comments or len(comments) == 0:
        return {"positive": 0, "neutral": 0, "negative": 0}, {
            "positive": [],
            "negative": []
        }
    
    # Filter out empty/invalid comments
    valid_comments = [c for c in comments if clean_comment(c)]
    
    if not valid_comments:
        return {"positive": 0, "neutral": 0, "negative": 0}, {
            "positive": [],
            "negative": []
        }
    
    labeled = [(c, analyze_sentiment(c)) for c in valid_comments]
    results = [label for _, label in labeled]
    total = len(results)
    count = Counter(results)

    summary = {
        "positive": round((count.get("positive", 0) / total) * 100, 1),
        "neutral": round((count.get("neutral", 0) / total) * 100, 1),
        "negative": round((count.get("negative", 0) / total) * 100, 1),
    }

    # Get diverse examples by taking from different parts of the list
    positive_comments = [c for c, label in labeled if label == "positive"]
    negative_comments = [c for c, label in labeled if label == "negative"]
    
    explanations = {
        "positive": positive_comments[:3] if len(positive_comments) >= 3 else positive_comments,
        "negative": negative_comments[:3] if len(negative_comments) >= 3 else negative_comments,
    }

    return summary, explanations
