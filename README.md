# Creator Business Management Dashboard

A comprehensive Streamlit application for managing YouTube creator partnerships, prospects, and outreach tracking with revenue analysis via YouTube API.

## Features

### 🤝 Partners Management
- Add and manage business partners with detailed information
- Track partnership types, revenue sharing agreements, and status
- View YouTube channel statistics and estimated revenue
- Convert prospects to partners seamlessly

### 🎯 Prospects Management
- Maintain a database of potential partners
- Track interest levels and interaction status
- Analyze prospect channel performance
- Add notes and manage follow-up activities

### 📧 Outreach Tracking
- Log all outreach activities with partners and prospects
- Track communication methods, response rates, and follow-ups
- Monitor revenue generated from outreach efforts
- Filter and analyze outreach performance

### 💰 Revenue Dashboard
- Estimate monthly revenue from partner channels
- Calculate revenue share based on partnership agreements
- Track outreach-generated revenue
- Annual revenue projections and analytics

### 📊 Analytics Overview
- Comprehensive metrics and KPIs
- Partner and prospect status distributions
- Sentiment analysis of partner channel comments
- Performance tracking across all activities

## Getting Started

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up your API keys in Streamlit secrets:
   - `YOUTUBE_API_KEY`: Your YouTube Data API key from [Google Developer Console](https://console.cloud.google.com/)

3. Launch the application:

   ```bash
   streamlit run app.py
   ```

## Usage

### Adding Partners
1. Navigate to **Partners Management**
2. Use **Add New Partner** to add creator partners
3. Specify partnership type, revenue share percentage, and contact details
4. View channel statistics and estimated revenue

### Managing Prospects
1. Go to **Prospects Management**
2. Add potential partners with their channel information
3. Track interest levels and interaction status
4. Convert successful prospects to partners

### Tracking Outreach
1. Use **Outreach Tracking** to log all communications
2. Record outreach method, response status, and generated revenue
3. Set follow-up dates and add detailed notes
4. Monitor response rates and ROI

### Revenue Analysis
1. Visit **Revenue Dashboard** for financial insights
2. View estimated monthly revenue from all partners
3. Track revenue share calculations
4. Monitor outreach-generated income

## Data Management

The application stores data in CSV files within the `data/` directory:
- `partners.csv`: Partner information and agreements
- `prospects.csv`: Potential partner database  
- `outreach_tracking.csv`: Communication logs and results

## YouTube API Integration

The dashboard integrates with YouTube Data API v3 to:
- Fetch channel statistics (subscribers, views, videos)
- Analyze comment sentiment on latest videos
- Estimate revenue based on channel performance
- Track channel growth and engagement

## Requirements

- Python 3.7+
- Streamlit
- pandas
- YouTube Data API v3 access
- Internet connection for API calls
