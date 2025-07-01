
import streamlit as st
import pandas as pd
from utils.news_alerts import fetch_news_mentions
from utils.sentiment_check import sentiment_summary
from utils.youtube_api import get_latest_video_id, get_comments

st.set_page_config(page_title="Creator Intelligence Dashboard", layout="wide")
st.title("🎬 YouTube Creator Intelligence Dashboard")

# Use secrets for API keys (Streamlit Cloud)
api_key_news = st.secrets["GNEWS_API_KEY"]
api_key_yt = st.secrets["YOUTUBE_API_KEY"]

# Load creator roster
csv_path = "data/creator_roster.csv"
try:
    df = pd.read_csv(csv_path)
    creator_names = df["Creator Name"].tolist()
    selected_creator = st.selectbox("Select a Creator", creator_names)
    creator_row = df[df["Creator Name"] == selected_creator].iloc[0]
    channel_id = creator_row["Channel ID"]

    # 📰 News Mentions
    st.header("📰 News Mentions")
    news_results = fetch_news_mentions(selected_creator, api_key_news)
    if news_results:
        for article in news_results:
            st.markdown(
                f"**{article['title']}**  \n"
                f"*{article['source']} - {article['publishedAt']}*  \n"
                f"{article['description']}  \n"
                f"[Read more]({article['url']})"
            )
    else:
        st.write("No recent news mentions found.")

    # 🧠 Sentiment Analysis
    st.header("🧠 Sentiment Analysis of Latest Video Comments")
    if channel_id:
        video_id = get_latest_video_id(channel_id, api_key_yt)
        if video_id:
            comments = get_comments(video_id, api_key_yt)
            if comments:
                summary, explanations = sentiment_summary(comments)

                col1, col2, col3 = st.columns(3)
                col1.metric("Positive", f"{summary['positive']}%")
                col2.metric("Neutral", f"{summary['neutral']}%")
                col3.metric("Negative", f"{summary['negative']}%")

                st.subheader("Example Positive Comments")
                for c in explanations["positive"]:
                    st.markdown(f"✅ *{c}*")

                st.subheader("Example Negative Comments")
                for c in explanations["negative"]:
                    st.markdown(f"⚠️ *{c}*")
            else:
                st.warning("No comments found on the latest video.")
        else:
            st.warning("Could not find the latest video for this channel.")
    else:
        st.info("No channel ID available.")

except FileNotFoundError:
    st.error(f"CSV file not found at: {csv_path}")
