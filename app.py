import datetime
import streamlit as st
import pandas as pd

from utils.news_alerts import fetch_news_mentions
from utils.sentiment_check import sentiment_summary
from utils.youtube_api import (
    get_latest_video_id,
    get_comments,
    search_channel_id,
)


st.set_page_config(page_title="Creator Intelligence Dashboard", layout="wide")
st.title("🎬 YouTube Creator Intelligence Dashboard")

# API keys are stored in Streamlit secrets when deployed
api_key_news = st.secrets["GNEWS_API_KEY"]
api_key_yt = st.secrets["YOUTUBE_API_KEY"]


csv_path = "data/creator_roster.csv"

@st.cache_data
def load_roster(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        cols = [
            "Creator Name",
            "Channel ID",
            "Notes",
            "Requests",
            "Priority",
            "Status",
            "Last Updated",
        ]
        return pd.DataFrame(columns=cols)


def save_roster(df, path):
    df.to_csv(path, index=False)


df = load_roster(csv_path)

tab_dash, tab_add, tab_edit, tab_remove = st.tabs(
    ["Dashboard", "Add Creator", "Edit Creator", "Remove Creator"]
)

with tab_dash:
    if df.empty:
        st.info("No creators in the roster yet.")
    else:
        creator_names = df["Creator Name"].tolist()
        selected_creator = st.selectbox("Select a Creator", creator_names)
        creator_row = df[df["Creator Name"] == selected_creator].iloc[0]
        channel_id = creator_row["Channel ID"]

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

with tab_add:
    st.header("Add a New Creator")
    with st.form("add_creator"):
        creator_name = st.text_input("Creator Name")
        channel_id_input = st.text_input(
            "Channel ID (leave blank to search by name)"
        )
        notes = st.text_area("Notes")
        requests_text = st.text_area("Requests")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        status = st.selectbox("Status", ["Pending", "In Progress"])
        submitted = st.form_submit_button("Add Creator")

    if submitted:
        channel_id = channel_id_input
        if not channel_id:
            channel_id = search_channel_id(creator_name, api_key_yt)

        if not channel_id:
            st.error("Channel ID could not be found. Please provide it manually.")
        else:
            new_row = {
                "Creator Name": creator_name,
                "Channel ID": channel_id,
                "Notes": notes,
                "Requests": requests_text,
                "Priority": priority,
                "Status": status,
                "Last Updated": datetime.date.today(),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_roster(df, csv_path)
            st.success(f"{creator_name} added to roster.")
            st.experimental_rerun()

with tab_edit:
    st.header("Edit Existing Creator")
    if df.empty:
        st.info("No creators available to edit.")
    else:
        creator_to_edit = st.selectbox("Select Creator", df["Creator Name"], key="edit")
        row = df[df["Creator Name"] == creator_to_edit].iloc[0]

        with st.form("edit_creator"):
            notes_edit = st.text_area("Notes", row["Notes"])
            requests_edit = st.text_area("Requests", row["Requests"])
            priority_edit = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(row["Priority"]),
            )
            status_edit = st.text_input("Status", row["Status"])
            submitted_edit = st.form_submit_button("Save Changes")

        if submitted_edit:
            df.loc[df["Creator Name"] == creator_to_edit, [
                "Notes",
                "Requests",
                "Priority",
                "Status",
                "Last Updated",
            ]] = [
                notes_edit,
                requests_edit,
                priority_edit,
                status_edit,
                datetime.date.today(),
            ]
            save_roster(df, csv_path)
            st.success(f"{creator_to_edit} updated.")
            st.experimental_rerun()

with tab_remove:
    st.header("Remove Creator")
    if df.empty:
        st.info("No creators available to remove.")
    else:
        creator_to_remove = st.selectbox(
            "Select Creator", df["Creator Name"], key="remove"
        )
        if st.button("Remove Creator"):
            df = df[df["Creator Name"] != creator_to_remove]
            save_roster(df, csv_path)
            st.success(f"{creator_to_remove} removed from roster.")
            st.experimental_rerun()

