
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import json
import streamlit as st
from functools import wraps
import time

def handle_gsheet_errors(func):
    """Decorator to handle common Google Sheets API errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except gspread.exceptions.APIError as e:
            print(f"Google Sheets API error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid credentials format: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in Google Sheets operation: {e}")
            return None
    return wrapper

@handle_gsheet_errors
def get_gsheet_client():
    """Get authenticated Google Sheets client with error handling."""
    try:
        credentials_dict = json.loads(st.secrets["GSHEET_SERVICE_ACCOUNT"])
        return gspread.service_account_from_dict(credentials_dict)
    except KeyError:
        print("Google Sheets credentials not found in secrets")
        return None

@handle_gsheet_errors
def read_roster_from_sheet(sheet_id):
    """Read creator roster from Google Sheet with error handling."""
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame(columns=["Creator Name", "Channel ID"])
    
    sheet = client.open_by_key(sheet_id).sheet1
    df = get_as_dataframe(sheet).dropna(how='all')
    
    # Ensure required columns exist
    required_columns = ["Creator Name", "Channel ID"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    return df[required_columns]

@handle_gsheet_errors
def add_creator_to_sheet(sheet_id, name, channel_id):
    """Add a creator to Google Sheet with error handling."""
    if not name or not channel_id:
        print("Invalid creator data provided")
        return False
    
    df = read_roster_from_sheet(sheet_id)
    if df is None:
        return False
    
    # Check for duplicates
    if name in df["Creator Name"].values:
        print(f"Creator {name} already exists in sheet")
        return False
    
    new_row = pd.DataFrame([[name.strip(), channel_id.strip()]], columns=["Creator Name", "Channel ID"])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    
    client = get_gsheet_client()
    if not client:
        return False
    
    sheet = client.open_by_key(sheet_id).sheet1
    set_with_dataframe(sheet, updated_df)
    return True

@handle_gsheet_errors
def remove_creator_from_sheet(sheet_id, name_to_remove):
    """Remove a creator from Google Sheet with error handling."""
    if not name_to_remove:
        print("No creator name provided for removal")
        return False
    
    df = read_roster_from_sheet(sheet_id)
    if df is None:
        return False
    
    if name_to_remove not in df["Creator Name"].values:
        print(f"Creator {name_to_remove} not found in sheet")
        return False
    
    df = df[df["Creator Name"] != name_to_remove]
    
    client = get_gsheet_client()
    if not client:
        return False
    
    sheet = client.open_by_key(sheet_id).sheet1
    set_with_dataframe(sheet, df)
    return True
