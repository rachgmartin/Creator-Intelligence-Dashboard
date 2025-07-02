
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import json
import streamlit as st

def get_gsheet_client():
    credentials_dict = json.loads(st.secrets["GSHEET_SERVICE_ACCOUNT"])
    return gspread.service_account_from_dict(credentials_dict)

def read_roster_from_sheet(sheet_id):
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id).sheet1
    df = get_as_dataframe(sheet).dropna(how='all')
    return df[["Creator Name", "Channel ID"]]

def add_creator_to_sheet(sheet_id, name, channel_id):
    df = read_roster_from_sheet(sheet_id)
    new_row = pd.DataFrame([[name, channel_id]], columns=["Creator Name", "Channel ID"])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id).sheet1
    set_with_dataframe(sheet, updated_df)

def remove_creator_from_sheet(sheet_id, name_to_remove):
    df = read_roster_from_sheet(sheet_id)
    df = df[df["Creator Name"] != name_to_remove]
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id).sheet1
    set_with_dataframe(sheet, df)
