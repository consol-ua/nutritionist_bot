from google.cloud import firestore
from datetime import datetime
from typing import Optional, Dict, Any
import google.auth

class FirestoreDB:
    def __init__(self):
        """
        Ініціалізує підключення до Firestore.

        Якщо код виконується в середовищі Google Cloud (наприклад, Cloud Run),
        клієнтська бібліотека автоматично використовує ідентифікацію сервісу.
        Якщо код виконується локально, потрібно налаштувати GOOGLE_APPLICATION_CREDENTIALS.
        """
        credentials, _ = google.auth.default()

        self.db = firestore.Client(credentials)
        self.users_collection = self.db.collection('users')
    
    def user_exists(self, user_id: int) -> bool:
        """Перевіряє чи існує користувач в базі даних"""
        doc = self.users_collection.document(str(user_id)).get()
        return doc.exists

    def add_user(self, user_data: Dict[str, Any]) -> None:
        """Додає нового користувача до бази даних"""
        user_data['created_at'] = datetime.now()
        self.users_collection.document(str(user_data['user_id'])).set(user_data)
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Отримує дані користувача за його ID"""
        doc = self.users_collection.document(str(user_id)).get()
        return doc.to_dict() if doc.exists else None
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> None:
        """Оновлює дані користувача"""
        self.users_collection.document(str(user_id)).update(data)
    
    def delete_user(self, user_id: int):
        """
        Видаляє користувача
        
        Args:
            user_id (int): Telegram ID користувача
        """
        self.users_collection.document(str(user_id)).delete()

# Створюємо глобальний екземпляр бази даних
db = FirestoreDB()
