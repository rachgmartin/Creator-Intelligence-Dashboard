
import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
from utils.youtube_api import (
    get_latest_video_id,
    get_comments,
    get_channel_stats,
    get_channel_title,
    get_video_stats,
    get_channel_revenue_estimate
)
from utils.sentiment_check import sentiment_summary

st.set_page_config(page_title="Creator Business Management Dashboard", layout="wide")
st.title("🎬 Creator Business Management Dashboard")

api_key_yt = st.secrets["YOUTUBE_API_KEY"]
partners_csv_path = "data/partners.csv"
prospects_csv_path = "data/prospects.csv"
outreach_csv_path = "data/outreach_tracking.csv"

def validate_name(name, field_name="Name"):
    """Validate name input."""
    if not name or not name.strip():
        return False, f"{field_name} cannot be empty"
    if len(name.strip()) > 100:
        return False, f"{field_name} too long (max 100 characters)"
    if not re.match(r'^[a-zA-Z0-9\s\-_.@#&]+$', name.strip()):
        return False, f"{field_name} contains invalid characters"
    return True, ""

def validate_channel_id(channel_id):
    """Validate YouTube channel ID format."""
    if not channel_id or not channel_id.strip():
        return False, "Channel ID cannot be empty"
    cleaned_id = channel_id.strip()
    if not re.match(r'^UC[a-zA-Z0-9_-]{22}$', cleaned_id):
        return False, "Invalid YouTube channel ID format (should start with UC and be 24 characters)"
    return True, ""

def validate_email(email):
    """Validate email format."""
    if not email or not email.strip():
        return False, "Email cannot be empty"
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
        return False, "Invalid email format"
    return True, ""

# Ensure data directory exists and initialize CSV files
os.makedirs(os.path.dirname(partners_csv_path), exist_ok=True)

# Initialize Partners CSV
if not os.path.exists(partners_csv_path):
    partners_df = pd.DataFrame(columns=["Partner Name", "Channel ID", "Email", "Partnership Type", "Revenue Share %", "Date Added", "Status"])
    partners_df.to_csv(partners_csv_path, index=False)
else:
    partners_df = pd.read_csv(partners_csv_path)

# Initialize Prospects CSV
if not os.path.exists(prospects_csv_path):
    prospects_df = pd.DataFrame(columns=["Prospect Name", "Channel ID", "Email", "Interest Level", "Notes", "Date Added", "Status"])
    prospects_df.to_csv(prospects_csv_path, index=False)
else:
    prospects_df = pd.read_csv(prospects_csv_path)

# Initialize Outreach Tracking CSV
if not os.path.exists(outreach_csv_path):
    outreach_df = pd.DataFrame(columns=["Contact Name", "Contact Type", "Outreach Date", "Method", "Response Status", "Follow-up Date", "Notes", "Revenue Generated"])
    outreach_df.to_csv(outreach_csv_path, index=False)
else:
    outreach_df = pd.read_csv(outreach_csv_path)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a section", [
    "Partners Management", 
    "Prospects Management", 
    "Outreach Tracking", 
    "Revenue Dashboard",
    "Analytics Overview"
])

if page == "Partners Management":
    st.header("🤝 Partners Management")
    
    # Add new partner
    with st.expander("➕ Add New Partner"):
        col1, col2 = st.columns(2)
        with col1:
            partner_name = st.text_input("Partner Name")
            channel_id = st.text_input("YouTube Channel ID")
            email = st.text_input("Email")
        with col2:
            partnership_type = st.selectbox("Partnership Type", 
                ["Brand Collaboration", "Content Creator", "Affiliate", "Sponsor", "Other"])
            revenue_share = st.number_input("Revenue Share %", min_value=0.0, max_value=100.0, step=0.1)
            status = st.selectbox("Status", ["Active", "Inactive", "Pending"])
        
        if st.button("Add Partner"):
            name_valid, name_msg = validate_name(partner_name, "Partner Name")
            channel_valid, channel_msg = validate_channel_id(channel_id)
            email_valid, email_msg = validate_email(email)
            
            if name_valid and channel_valid and email_valid:
                new_partner = pd.DataFrame([[
                    partner_name, channel_id, email, partnership_type, 
                    revenue_share, datetime.now().strftime("%Y-%m-%d"), status
                ]], columns=partners_df.columns)
                partners_df = pd.concat([partners_df, new_partner], ignore_index=True)
                partners_df.to_csv(partners_csv_path, index=False)
                st.success(f"Partner {partner_name} added successfully!")
                st.rerun()
            else:
                if not name_valid:
                    st.error(name_msg)
                if not channel_valid:
                    st.error(channel_msg)
                if not email_valid:
                    st.error(email_msg)
    
    # Display and manage partners
    if not partners_df.empty:
        st.subheader("Current Partners")
        
        # Partner selection and management
        selected_partner = st.selectbox("Select Partner", partners_df["Partner Name"].tolist())
        partner_row = partners_df[partners_df["Partner Name"] == selected_partner].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Partnership Type", partner_row["Partnership Type"])
        with col2:
            st.metric("Revenue Share", f"{partner_row['Revenue Share %']}%")
        with col3:
            st.metric("Status", partner_row["Status"])
        
        # Partner channel stats
        if partner_row["Channel ID"]:
            st.subheader(f"📈 {selected_partner} Channel Stats")
            stats = get_channel_stats(partner_row["Channel ID"], api_key_yt)
            if stats:
                col1, col2, col3 = st.columns(3)
                col1.metric("Subscribers", f"{int(stats['subscribers']):,}" if stats['subscribers'] else "N/A")
                col2.metric("Total Views", f"{int(stats['views']):,}" if stats['views'] else "N/A")
                col3.metric("Total Videos", stats['videos'] or "N/A")
                
                # Revenue estimate
                revenue_estimate = get_channel_revenue_estimate(partner_row["Channel ID"], api_key_yt)
                if revenue_estimate:
                    st.metric("Estimated Monthly Revenue", f"${revenue_estimate:,.2f}")
        
        # Remove partner
        with st.expander("🗑️ Remove Partner"):
            if st.button(f"Remove {selected_partner}"):
                partners_df = partners_df[partners_df["Partner Name"] != selected_partner]
                partners_df.to_csv(partners_csv_path, index=False)
                st.success(f"{selected_partner} removed.")
                st.rerun()
        
        # Display partners table
        st.dataframe(partners_df)
    else:
        st.info("No partners added yet.")

elif page == "Prospects Management":
    st.header("🎯 Prospects Management")
    
    # Add new prospect
    with st.expander("➕ Add New Prospect"):
        col1, col2 = st.columns(2)
        with col1:
            prospect_name = st.text_input("Prospect Name")
            prospect_channel_id = st.text_input("YouTube Channel ID")
            prospect_email = st.text_input("Email")
        with col2:
            interest_level = st.selectbox("Interest Level", ["High", "Medium", "Low", "Unknown"])
            prospect_status = st.selectbox("Status", ["New", "Contacted", "Interested", "Not Interested", "Converted"])
            notes = st.text_area("Notes")
        
        if st.button("Add Prospect"):
            name_valid, name_msg = validate_name(prospect_name, "Prospect Name")
            channel_valid, channel_msg = validate_channel_id(prospect_channel_id)
            email_valid, email_msg = validate_email(prospect_email)
            
            if name_valid and channel_valid and email_valid:
                new_prospect = pd.DataFrame([[
                    prospect_name, prospect_channel_id, prospect_email, interest_level, 
                    notes, datetime.now().strftime("%Y-%m-%d"), prospect_status
                ]], columns=prospects_df.columns)
                prospects_df = pd.concat([prospects_df, new_prospect], ignore_index=True)
                prospects_df.to_csv(prospects_csv_path, index=False)
                st.success(f"Prospect {prospect_name} added successfully!")
                st.rerun()
            else:
                if not name_valid:
                    st.error(name_msg)
                if not channel_valid:
                    st.error(channel_msg)
                if not email_valid:
                    st.error(email_msg)
    
    # Display and manage prospects
    if not prospects_df.empty:
        st.subheader("Current Prospects")
        
        # Prospect selection and management
        selected_prospect = st.selectbox("Select Prospect", prospects_df["Prospect Name"].tolist())
        prospect_row = prospects_df[prospects_df["Prospect Name"] == selected_prospect].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Interest Level", prospect_row["Interest Level"])
        with col2:
            st.metric("Status", prospect_row["Status"])
        with col3:
            st.metric("Date Added", prospect_row["Date Added"])
        
        # Prospect channel stats
        if prospect_row["Channel ID"]:
            st.subheader(f"📈 {selected_prospect} Channel Stats")
            stats = get_channel_stats(prospect_row["Channel ID"], api_key_yt)
            if stats:
                col1, col2, col3 = st.columns(3)
                col1.metric("Subscribers", f"{int(stats['subscribers']):,}" if stats['subscribers'] else "N/A")
                col2.metric("Total Views", f"{int(stats['views']):,}" if stats['views'] else "N/A")
                col3.metric("Total Videos", stats['videos'] or "N/A")
                
                # Revenue estimate
                revenue_estimate = get_channel_revenue_estimate(prospect_row["Channel ID"], api_key_yt)
                if revenue_estimate:
                    st.metric("Estimated Monthly Revenue", f"${revenue_estimate:,.2f}")
        
        # Convert to partner
        with st.expander("🤝 Convert to Partner"):
            if st.button(f"Convert {selected_prospect} to Partner"):
                # Add to partners
                new_partner = pd.DataFrame([[
                    prospect_row["Prospect Name"], prospect_row["Channel ID"], prospect_row["Email"], 
                    "Content Creator", 0.0, datetime.now().strftime("%Y-%m-%d"), "Active"
                ]], columns=partners_df.columns)
                partners_df = pd.concat([partners_df, new_partner], ignore_index=True)
                partners_df.to_csv(partners_csv_path, index=False)
                
                # Remove from prospects
                prospects_df = prospects_df[prospects_df["Prospect Name"] != selected_prospect]
                prospects_df.to_csv(prospects_csv_path, index=False)
                
                st.success(f"{selected_prospect} converted to partner!")
                st.rerun()
        
        # Remove prospect
        with st.expander("🗑️ Remove Prospect"):
            if st.button(f"Remove {selected_prospect}"):
                prospects_df = prospects_df[prospects_df["Prospect Name"] != selected_prospect]
                prospects_df.to_csv(prospects_csv_path, index=False)
                st.success(f"{selected_prospect} removed.")
                st.rerun()
        
        # Display prospects table
        st.dataframe(prospects_df)
    else:
        st.info("No prospects added yet.")

elif page == "Outreach Tracking":
    st.header("📧 Outreach Tracking")
    
    # Add new outreach record
    with st.expander("➕ Log New Outreach"):
        col1, col2 = st.columns(2)
        with col1:
            contact_name = st.selectbox("Contact Name", 
                list(partners_df["Partner Name"]) + list(prospects_df["Prospect Name"]) if not partners_df.empty or not prospects_df.empty else ["No contacts available"])
            contact_type = st.selectbox("Contact Type", ["Partner", "Prospect"])
            outreach_date = st.date_input("Outreach Date", datetime.now().date())
            method = st.selectbox("Method", ["Email", "Phone", "Social Media", "In Person", "Video Call"])
        with col2:
            response_status = st.selectbox("Response Status", ["Sent", "Opened", "Replied", "No Response", "Interested", "Not Interested"])
            follow_up_date = st.date_input("Follow-up Date", datetime.now().date())
            revenue_generated = st.number_input("Revenue Generated ($)", min_value=0.0, step=0.01)
            outreach_notes = st.text_area("Notes")
        
        if st.button("Log Outreach"):
            if contact_name != "No contacts available":
                new_outreach = pd.DataFrame([[
                    contact_name, contact_type, outreach_date.strftime("%Y-%m-%d"), method, 
                    response_status, follow_up_date.strftime("%Y-%m-%d"), outreach_notes, revenue_generated
                ]], columns=outreach_df.columns)
                outreach_df = pd.concat([outreach_df, new_outreach], ignore_index=True)
                outreach_df.to_csv(outreach_csv_path, index=False)
                st.success("Outreach logged successfully!")
                st.rerun()
            else:
                st.error("Please add partners or prospects first.")
    
    # Display outreach records
    if not outreach_df.empty:
        st.subheader("Outreach History")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_contact = st.selectbox("Filter by Contact", ["All"] + list(outreach_df["Contact Name"].unique()))
        with col2:
            filter_method = st.selectbox("Filter by Method", ["All"] + list(outreach_df["Method"].unique()))
        with col3:
            filter_status = st.selectbox("Filter by Status", ["All"] + list(outreach_df["Response Status"].unique()))
        
        # Apply filters
        filtered_df = outreach_df.copy()
        if filter_contact != "All":
            filtered_df = filtered_df[filtered_df["Contact Name"] == filter_contact]
        if filter_method != "All":
            filtered_df = filtered_df[filtered_df["Method"] == filter_method]
        if filter_status != "All":
            filtered_df = filtered_df[filtered_df["Response Status"] == filter_status]
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Outreach", len(filtered_df))
        with col2:
            replied_count = len(filtered_df[filtered_df["Response Status"] == "Replied"])
            st.metric("Replied", replied_count)
        with col3:
            response_rate = (replied_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("Response Rate", f"{response_rate:.1f}%")
        with col4:
            total_revenue = filtered_df["Revenue Generated"].sum()
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        
        st.dataframe(filtered_df)
    else:
        st.info("No outreach records logged yet.")

elif page == "Revenue Dashboard":
    st.header("💰 Revenue Dashboard")
    
    if not partners_df.empty:
        st.subheader("Partner Revenue Analysis")
        
        total_estimated_revenue = 0
        partner_revenue_data = []
        
        for _, partner in partners_df.iterrows():
            if partner["Channel ID"]:
                revenue_estimate = get_channel_revenue_estimate(partner["Channel ID"], api_key_yt)
                if revenue_estimate:
                    partner_share = revenue_estimate * (partner["Revenue Share %"] / 100)
                    total_estimated_revenue += partner_share
                    partner_revenue_data.append({
                        "Partner": partner["Partner Name"],
                        "Estimated Monthly Revenue": revenue_estimate,
                        "Your Share": partner_share,
                        "Revenue Share %": partner["Revenue Share %"]
                    })
        
        if partner_revenue_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Monthly Revenue Share", f"${total_estimated_revenue:,.2f}")
            with col2:
                st.metric("Annual Revenue Projection", f"${total_estimated_revenue * 12:,.2f}")
            with col3:
                active_partners = len(partners_df[partners_df["Status"] == "Active"])
                st.metric("Active Partners", active_partners)
            
            revenue_df = pd.DataFrame(partner_revenue_data)
            st.dataframe(revenue_df)
            
            # Revenue chart
            st.subheader("Revenue by Partner")
            st.bar_chart(revenue_df.set_index("Partner")["Your Share"])
        
        # Outreach revenue
        if not outreach_df.empty:
            st.subheader("Outreach Generated Revenue")
            outreach_revenue = outreach_df["Revenue Generated"].sum()
            monthly_outreach_revenue = outreach_df[outreach_df["Outreach Date"] >= (datetime.now() - pd.Timedelta(days=30))]["Revenue Generated"].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Outreach Revenue", f"${outreach_revenue:,.2f}")
            with col2:
                st.metric("Last 30 Days", f"${monthly_outreach_revenue:,.2f}")
    else:
        st.info("Add partners to see revenue analysis.")

elif page == "Analytics Overview":
    st.header("📊 Analytics Overview")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Partners", len(partners_df) if not partners_df.empty else 0)
    with col2:
        st.metric("Total Prospects", len(prospects_df) if not prospects_df.empty else 0)
    with col3:
        st.metric("Total Outreach", len(outreach_df) if not outreach_df.empty else 0)
    with col4:
        active_partners = len(partners_df[partners_df["Status"] == "Active"]) if not partners_df.empty else 0
        st.metric("Active Partners", active_partners)
    
    # Sentiment analysis for active partners
    if not partners_df.empty:
        st.subheader("🧠 Partner Sentiment Analysis")
        partner_for_sentiment = st.selectbox("Select Partner for Comment Analysis", 
            partners_df[partners_df["Status"] == "Active"]["Partner Name"].tolist() if active_partners > 0 else ["No active partners"])
        
        if partner_for_sentiment != "No active partners":
            partner_row = partners_df[partners_df["Partner Name"] == partner_for_sentiment].iloc[0]
            channel_id = partner_row["Channel ID"]
            
            video_id = get_latest_video_id(channel_id, api_key_yt)
            if video_id:
                comments = get_comments(video_id, api_key_yt)
                if comments:
                    summary, explanations = sentiment_summary(comments)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Positive", f"{summary['positive']}%")
                    col2.metric("Neutral", f"{summary['neutral']}%")
                    col3.metric("Negative", f"{summary['negative']}%")
                    
                    if explanations["positive"]:
                        st.subheader("Example Positive Comments")
                        for c in explanations["positive"][:3]:
                            st.markdown(f"✅ *{c}*")
                    
                    if explanations["negative"]:
                        st.subheader("Example Negative Comments")
                        for c in explanations["negative"][:3]:
                            st.markdown(f"⚠️ *{c}*")
                else:
                    st.warning("No comments found on the latest video.")
            else:
                st.warning("Could not find the latest video for this channel.")
    
    # Status distribution charts
    if not partners_df.empty:
        st.subheader("Partner Status Distribution")
        status_counts = partners_df["Status"].value_counts()
        st.bar_chart(status_counts)
    
    if not prospects_df.empty:
        st.subheader("Prospect Interest Level Distribution")
        interest_counts = prospects_df["Interest Level"].value_counts()
        st.bar_chart(interest_counts)
