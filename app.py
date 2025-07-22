
import streamlit as st
import pandas as pd
import os
import re

from utils.sentiment_check import sentiment_summary
from utils.youtube_api import (
    get_latest_video_id,
    get_comments,
    get_channel_stats,
    get_channel_title,
)

st.set_page_config(page_title="Creator Intelligence Dashboard", layout="wide")
st.title("🎬 YouTube Creator Intelligence Dashboard")

# Check for required API keys
try:
    api_key_yt = st.secrets["YOUTUBE_API_KEY"]
except KeyError as e:
    st.error(f"Missing required API key: {e}. Please configure your secrets.")
    st.stop()

csv_path = "data/creator_roster.csv"

def validate_creator_name(name):
    """Validate creator name input."""
    if not name or not name.strip():
        return False, "Creator name cannot be empty"
    if len(name.strip()) > 100:
        return False, "Creator name too long (max 100 characters)"
    # Allow letters, numbers, spaces, and common punctuation
    if not re.match(r'^[a-zA-Z0-9\s\-_.@#&]+$', name.strip()):
        return False, "Creator name contains invalid characters"
    return True, ""

def validate_channel_id(channel_id):
    """Validate YouTube channel ID format."""
    if not channel_id or not channel_id.strip():
        return False, "Channel ID cannot be empty"
    # YouTube channel IDs are typically 24 characters starting with UC
    cleaned_id = channel_id.strip()
    if not re.match(r'^UC[a-zA-Z0-9_-]{22}$', cleaned_id):
        return False, "Invalid YouTube channel ID format (should start with UC and be 24 characters)"
    return True, ""

# Ensure data directory exists and load or create the CSV
os.makedirs(os.path.dirname(csv_path), exist_ok=True)
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
        # Validate inputs
        name_valid, name_error = validate_creator_name(new_name)
        channel_valid, channel_error = validate_channel_id(new_channel_id)
        
        if not name_valid:
            st.error(f"Invalid creator name: {name_error}")
        elif not channel_valid:
            st.error(f"Invalid channel ID: {channel_error}")
        elif new_name.strip() in df["Creator Name"].values:
            st.error("Creator already exists!")
        else:
            new_entry = pd.DataFrame([[new_name.strip(), new_channel_id.strip()]], columns=["Creator Name", "Channel ID"])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(csv_path, index=False)
            st.success(f"{new_name.strip()} added successfully!")
            st.rerun()

# 🗑️ Remove a creator
with st.expander("🗑️ Remove a Creator"):
    if not df.empty:
        to_remove = st.selectbox("Select Creator to Remove", df["Creator Name"].tolist())
        if st.button("Remove Creator"):
            df = df[df["Creator Name"] != to_remove]
            df.to_csv(csv_path, index=False)
            st.success(f"{to_remove} removed.")
            st.rerun()

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
    with st.spinner("Fetching channel statistics..."):
        stats = get_channel_stats(channel_id, api_key_yt)
        if stats:
            col1, col2, col3 = st.columns(3)
            col1.metric("Subscribers", stats["subscribers"])
            col2.metric("Total Views", stats["views"])
            col3.metric("Total Videos", stats["videos"])
        else:
            st.warning("Could not fetch channel statistics. Please check the channel ID.")



    # Sentiment Summary
    st.subheader("🧠 Sentiment Analysis of Latest Video Comments")
    with st.spinner("Analyzing sentiment of latest video comments..."):
        video_id = get_latest_video_id(channel_id, api_key_yt)
        if video_id:
            comments = get_comments(video_id, api_key_yt)
            if comments:
                summary, explanations = sentiment_summary(comments)

                col1, col2, col3 = st.columns(3)
                col1.metric("Positive", f"{summary['positive']}%", delta=None)
                col2.metric("Neutral", f"{summary['neutral']}%", delta=None)
                col3.metric("Negative", f"{summary['negative']}%", delta=None)

                if explanations["positive"]:
                    st.subheader("Example Positive Comments")
                    for c in explanations["positive"]:
                        st.markdown(f"✅ *{c[:200]}{'...' if len(c) > 200 else ''}*")

                if explanations["negative"]:
                    st.subheader("Example Negative Comments")
                    for c in explanations["negative"]:
                        st.markdown(f"⚠️ *{c[:200]}{'...' if len(c) > 200 else ''}*")
                        
                st.info(f"Analysis based on {len(comments)} comments from the latest video.")
            else:
                st.warning("No comments found on the latest video.")
        else:
            st.warning("Could not find the latest video for this channel. Please verify the channel ID.")
else:
    st.info("No creators added yet. Use the expander above to add one.")
