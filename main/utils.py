# utils.py
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CRED = os.getenv("GOOGLE_SHEETS_CRED")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

def get_sheet():
    """
    Отримує доступ до Google Sheet.
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CRED, scopes=scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def user_exists(sheet, user_id):
    """
    Перевіряє, чи існує користувач у таблиці.

    Args:
        sheet: Аркуш Google Sheet.
        user_id: ID користувача Telegram.

    Returns:
        True, якщо користувач існує, інакше False.
    """
    records = sheet.get_all_records()
    print(f"Значення records: {records}")  # Виводимо значення records
    return any(str(row.get("UserID")) == str(user_id) for row in records)