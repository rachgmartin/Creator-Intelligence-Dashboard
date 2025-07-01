from textblob import TextBlob
from collections import Counter

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"

def sentiment_summary(comments):
    results = [analyze_sentiment(comment) for comment in comments]
    total = len(results)
    count = Counter(results)
    if total == 0:
        return {"positive": 0, "neutral": 0, "negative": 0}, []

    summary = {
        "positive": round((count["positive"] / total) * 100, 1),
        "neutral": round((count["neutral"] / total) * 100, 1),
        "negative": round((count["negative"] / total) * 100, 1)
    }

    explanations = {
        "positive": [c for c in comments if analyze_sentiment(c) == "positive"][:3],
        "negative": [c for c in comments if analyze_sentiment(c) == "negative"][:3]
    }

    return summary, explanations
