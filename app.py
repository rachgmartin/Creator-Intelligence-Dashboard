
import streamlit as st
import pandas as pd
import os
from utils.news_alerts import fetch_news_mentions
from utils.sentiment_check import sentiment_summary
from utils.youtube_api import (
    get_latest_video_id,
    get_comments,
    get_channel_stats,
    get_channel_title,
)

st.set_page_config(page_title="Creator Intelligence Dashboard", layout="wide")
st.title("🎬 YouTube Creator Intelligence Dashboard")

api_key_news = st.secrets["GNEWS_API_KEY"]
api_key_yt = st.secrets["YOUTUBE_API_KEY"]
csv_path = "data/creator_roster.csv"

# Load or create the CSV
if not os.path.exists(csv_path):
    df = pd.DataFrame(columns=["Creator Name", "Channel ID"])
    df.to_csv(csv_path, index=False)
else:
    df = pd.read_csv(csv_path)

# -----------------------------
# ➕ Add a new creator
with st.expander("➕ Add a New Creator"):
    new_name = st.text_input("Creator Name")
    new_channel_id = st.text_input("Channel ID")
    if st.button("Add Creator"):
        if new_name and new_channel_id:
            new_entry = pd.DataFrame([[new_name, new_channel_id]], columns=["Creator Name", "Channel ID"])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(csv_path, index=False)
            st.success(f"{new_name} added successfully!")
            st.experimental_rerun()

# 🗑️ Remove a creator
with st.expander("🗑️ Remove a Creator"):
    if not df.empty:
        to_remove = st.selectbox("Select Creator to Remove", df["Creator Name"].tolist())
        if st.button("Remove Creator"):
            df = df[df["Creator Name"] != to_remove]
            df.to_csv(csv_path, index=False)
            st.success(f"{to_remove} removed.")
            st.experimental_rerun()

# ---------------------------------
# Main Dashboard
if not df.empty:
    st.header("📊 Creator Overview")
    creator_names = df["Creator Name"].tolist()
    selected_creator = st.selectbox("Select a Creator", creator_names)
    creator_row = df[df["Creator Name"] == selected_creator].iloc[0]
    channel_id = creator_row["Channel ID"]

    # Channel Stats
    st.subheader("📈 Channel Stats")
    stats = get_channel_stats(channel_id, api_key_yt)
    if stats:
        col1, col2, col3 = st.columns(3)
        col1.metric("Subscribers", stats["subscribers"])
        col2.metric("Total Views", stats["views"])
        col3.metric("Total Videos", stats["videos"])
    else:
        st.warning("Could not fetch channel statistics.")

    # News Mentions
    st.subheader("📰 News Mentions")
    channel_name = get_channel_title(channel_id, api_key_yt) or selected_creator
    news_results = fetch_news_mentions(selected_creator, channel_name, api_key_news)
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

    # Sentiment Summary
    st.subheader("🧠 Sentiment Analysis of Latest Video Comments")
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
    st.info("No creators added yet. Use the expander above to add one.")
