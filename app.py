
import streamlit as st
import pandas as pd
import os
from utils.news_alerts import fetch_news_mentions
from utils.sentiment_check import sentiment_summary
from utils.youtube_api import (
    get_latest_video_id,
    get_comments,
    search_channel_id,
)

# Mock data for comments per creator
mock_comments = {
    "JaneDoe": [
        "I love her new video! So funny and relatable.",
        "This is so helpful, thank you!",
        "Not really a fan of this one, kinda boring.",
        "She’s always so positive and uplifting.",
        "Didn’t enjoy this, seemed rushed and lazy.",
        "Absolutely amazing content!"
    ],
    "JohnSmith": [
        "Why does he talk so slow?",
        "Great podcast episode, very insightful.",
        "Terrible editing, I couldn’t finish it.",
        "I look forward to these every week!",
        "Neutral on this one. Just okay.",
        "Worst upload yet. Unsubscribed."
    ]
}

st.set_page_config(page_title="Creator Intelligence Dashboard", layout="wide")
st.title("🎬 YouTube Creator Intelligence Dashboard")

# Path to roster CSV relative to this file
csv_path = os.path.join(os.path.dirname(__file__), "data", "creator_roster.csv")

try:
    df = pd.read_csv(csv_path)
    if "creator_names" not in st.session_state:
        st.session_state["creator_names"] = df["Creator Name"].tolist()
    if "new_channel" not in st.session_state:
        st.session_state["new_channel"] = ""

    # API keys
    yt_api_key = st.text_input("Enter your YouTube API Key", type="password")

    # Creator selection
    selected_creator = st.selectbox("Select a Creator", st.session_state.creator_names)

    # --- Add New Creator ---
    with st.expander("Add a New Creator"):
        new_name = st.text_input("Creator Name", key="new_creator")
        new_channel = st.text_input(
            "Channel ID",
            key="new_channel_input",
            value=st.session_state.get("new_channel", ""),
        )
        if yt_api_key and st.button("Search Channel ID"):
            try:
                found = search_channel_id(new_name, yt_api_key)
            except Exception:
                found = None
            if found:
                st.session_state["new_channel"] = found
                st.success(f"Found channel ID: {found}")
            else:
                st.warning("Channel not found.")
        if st.button("Add Creator"):
            if new_name and new_name not in st.session_state.creator_names:
                new_row = {
                    "Creator Name": new_name,
                    "Channel ID": st.session_state.get("new_channel", new_channel),
                    "Notes": "",
                    "Requests": "",
                    "Priority": "",
                    "Status": "",
                    "Last Updated": pd.Timestamp.today().date(),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(csv_path, index=False)
                st.session_state.creator_names.append(new_name)
                st.session_state["new_channel"] = ""
                st.experimental_rerun()

    # --- Manage Roster ---
    with st.expander("Manage Roster"):
        search_term = st.text_input("Search Roster", key="roster_search")
        if search_term:
            roster_view = df[df["Creator Name"].str.contains(search_term, case=False, na=False)]
        else:
            roster_view = df
        st.dataframe(roster_view)

        remove_choice = st.selectbox("Remove Creator", st.session_state.creator_names, key="remove_creator")
        if st.button("Delete Creator"):
            df = df[df["Creator Name"] != remove_choice]
            df.to_csv(csv_path, index=False)
            st.session_state.creator_names.remove(remove_choice)
            st.experimental_rerun()

    # GNews API Key input
    api_key = st.text_input("Enter your GNews API Key", type="password")

    # Show news mentions
    st.header("📰 News Mentions")
    if api_key:
        news_results = fetch_news_mentions(selected_creator, api_key)
        if news_results:
            for article in news_results:
                st.markdown(
                    f"**{article['title']}**\n"
                    f"*{article['source']} - {article['publishedAt']}*\n"
                    f"{article['description']}\n"
                    f"[Read more]({article['url']})"
                )
        else:
            st.write("No recent news mentions found.")
    else:
        st.warning("Please enter your GNews API key to view news mentions.")

    # Sentiment summary
    st.header("🧠 Sentiment Analysis of Recent Comments")
    comments = []
    if yt_api_key:
        channel_row = df[df["Creator Name"] == selected_creator]
        if not channel_row.empty:
            channel_id = channel_row.iloc[0]["Channel ID"]
            video_id = get_latest_video_id(channel_id, yt_api_key)
            if video_id:
                comments = get_comments(video_id, yt_api_key)
    if not comments:
        comments = mock_comments.get(selected_creator, [])
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

except FileNotFoundError:
    st.error(f"CSV file not found at: {csv_path}")
