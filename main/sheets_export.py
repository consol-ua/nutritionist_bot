import gspread
from database import db
import google.auth

def get_sheet():
    """Підключається до Google Sheets та повертає об'єкт таблиці"""
    # Використовуємо вбудовані облікові дані Google Cloud Run
    credentials, _ = google.auth.default()
    
    gc = gspread.authorize(credentials)
    sheet_name = 'Nutritionist-user-data'  # Фіксована назва таблиці
    
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
    headers = ['ID', 'First Name', 'Last Name', 'Username', 'Phone', 'Registration Date']
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