
import streamlit as st
import pandas as pd
import os
from utils.news_alerts import fetch_news_mentions
from utils.sentiment_check import sentiment_summary
from utils.youtube_api import get_latest_video_id, get_comments

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
        st.session_state.creator_names = df["Creator Name"].tolist()

    # Creator selection
    selected_creator = st.selectbox("Select a Creator", st.session_state.creator_names)

    # --- Add New Creator ---
    with st.expander("Add a New Creator"):
        new_name = st.text_input("Creator Name", key="new_creator")
        if st.button("Add Creator"):
            if new_name and new_name not in st.session_state.creator_names:
                new_row = {
                    "Creator Name": new_name,
                    "Channel ID": "",
                    "Notes": "",
                    "Requests": "",
                    "Priority": "",
                    "Status": "",
                    "Last Updated": pd.Timestamp.today().date(),
                }
                df = df.append(new_row, ignore_index=True)
                df.to_csv(csv_path, index=False)
                st.session_state.creator_names.append(new_name)
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
                    f"""**{article['title']}**
*{article['source']} - {article['publishedAt']}*
{article['description']}
[Read more]({article['url']})"""
                )
        else:
            st.write("No recent news mentions found.")
    else:
        st.warning("Please enter your GNews API key to view news mentions.")

    # Sentiment summary
    st.header("🧠 Sentiment Analysis of Recent Comments")
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
