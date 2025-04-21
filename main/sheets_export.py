import gspread
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from database import db

load_dotenv()

def get_sheet():
    """Підключається до Google Sheets та повертає об'єкт таблиці"""
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS не встановлено в .env файлі")
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    gc = gspread.authorize(credentials)
    sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Nutritionist-user-data')
    
    try:
        sheet = gc.open(sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        sheet = gc.create(sheet_name)
        sheet.share(None, perm_type='anyone', role='reader')
    
    return sheet.sheet1

def export_users_to_sheet():
    """Експортує всіх користувачів з Firestore в Google Sheets"""
    sheet = get_sheet()
    
    # Очищаємо таблицю, залишаючи заголовки
    sheet.clear()
    
    # Додаємо заголовки
    headers = ['ID', 'Ім\'я', 'Прізвище', 'Username', 'Телефон', 'Дата реєстрації']
    sheet.append_row(headers)
    
    # Отримуємо всіх користувачів з Firestore
    users = db.users_collection.stream()
    
    # Додаємо дані користувачів
    for user in users:
        user_data = user.to_dict()
        row = [
            user_data.get('user_id', ''),
            user_data.get('first_name', ''),
            user_data.get('last_name', ''),
            user_data.get('username', ''),
            user_data.get('phone', ''),
            user_data.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if user_data.get('created_at') else ''
        ]
        sheet.append_row(row)
    
    return f"✅ Експортовано {sheet.row_count - 1} користувачів в Google Sheets" 