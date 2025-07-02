# YouTube Creator Intelligence Dashboard

A Streamlit app for managing and monitoring a roster of YouTube creators. Tracks performance, requests, news mentions, and sentiment analysis.

Recent updates ensure that the latest video comments are properly retrieved for sentiment analysis and that news alerts search by both a creator's name and their channel title for more relevant results.

## Getting Started

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Launch the application using Streamlit:

   ```bash
   streamlit run app.py
   ```

## Adding Real Creators

1. Obtain a YouTube Data API key from the [Google Developer Console](https://console.cloud.google.com/).
2. Launch the Streamlit app and enter your API key when prompted.
3. Use the **Add a New Creator** section to search for a channel by name or paste a known channel ID.
4. Click **Add Creator** to save them to your roster.
5. Use **Edit Existing Creator** to update notes, requests, or status values.
6. Use **Remove Creator** to delete a creator from the roster.
7. When you select a creator on the dashboard, recent comments will be fetched from their latest video using your API key.
