import gspread
from database import db
import google.auth

def get_sheet(sheet_url=None):
    """Підключається до Google Sheets та повертає об'єкт таблиці"""
    # Використовуємо вбудовані облікові дані Google Cloud Run
    credentials, _ = google.auth.default()
    
    gc = gspread.authorize(credentials)
    
    if sheet_url:
        try:
            sheet = gc.open_by_url(sheet_url)
            return sheet.sheet1, sheet.url
        except Exception as e:
            raise Exception(f"❌ Помилка при відкритті таблиці: {str(e)}")
    else:
        sheet_name = 'Nutritionist-user-data'  # Фіксована назва таблиці
        try:
            sheet = gc.open(sheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            sheet = gc.create(sheet_name)
            sheet.share(None, perm_type='anyone', role='reader')
        
        return sheet.sheet1, sheet.url

def export_users_to_sheet(sheet_url=None):
    """Експортує всіх користувачів з Firestore в Google Sheets"""
    sheet, sheet_url = get_sheet(sheet_url)
    
    # Очищаємо таблицю, залишаючи заголовки
    sheet.clear()
    
    # Додаємо заголовки
    headers = ['ID', 'First Name', 'Last Name', 'Username', 'Phone', 'Registration Date']
    sheet.append_row(headers)
    
    # Отримуємо всіх користувачів з Firestore
    users = db.users_collection.stream()
    users_list = list(users)  # Конвертуємо в список для підрахунку
    
    # Додаємо дані користувачів
    for user in users_list:
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
    
    total_users = len(users_list)
    return f"✅ Експортовано {total_users} користувачів в Google Sheets\n\n🔗 Посилання на таблицю: {sheet_url}" 