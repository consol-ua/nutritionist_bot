# utils.py
import gspread
import google.auth
import os
from dotenv import load_dotenv

load_dotenv()

SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

def get_sheet():
    """
    Отримує доступ до Google Sheet, використовуючи автентифікацію за замовчуванням Google Cloud.
    """
    try:
        creds, _ = google.auth.default()
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"Помилка автентифікації Google Cloud: {e}")
        raise

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