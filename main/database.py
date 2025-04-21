from google.cloud import firestore
from datetime import datetime
from typing import Optional, Dict, Any

class FirestoreDB:
    def __init__(self):
        """
        Ініціалізує підключення до Firestore.

        Якщо код виконується в середовищі Google Cloud (наприклад, Cloud Run),
        клієнтська бібліотека автоматично використовує ідентифікацію сервісу.
        Якщо код виконується локально, потрібно налаштувати GOOGLE_APPLICATION_CREDENTIALS.
        """
        self.db = firestore.Client()  # Клієнтська бібліотека обробляє аутентифікацію
        self.users_collection = self.db.collection('users')
        self.sessions_collection = self.db.collection('sessions')
        self.meals_collection = self.db.collection('meals')
        self.nutrition_plans_collection = self.db.collection('nutrition_plans')
    
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

    def add_session(self, session_data: Dict[str, Any]) -> None:
        """Додає нову сесію"""
        session_data['created_at'] = datetime.now()
        self.sessions_collection.add(session_data)

    def add_meal(self, meal_data: Dict[str, Any]) -> None:
        """Додає новий прийом їжі"""
        meal_data['created_at'] = datetime.now()
        self.meals_collection.add(meal_data)

    def add_nutrition_plan(self, plan_data: Dict[str, Any]) -> None:
        """Додає новий план харчування"""
        plan_data['created_at'] = datetime.now()
        self.nutrition_plans_collection.add(plan_data)

# Створюємо глобальний екземпляр бази даних
db = FirestoreDB()
