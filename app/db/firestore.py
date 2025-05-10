from google.cloud import firestore
from ..core.config import get_settings
from ..core.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class FirestoreClient:
    def __init__(self):
        credentials = settings.get_google_credentials()
        if credentials:
            self.client = firestore.Client(
                project=settings.PROJECT_ID,
                credentials=firestore.Client.from_service_account_file(
                    credentials["credentials_file"]
                )
            )
        else:
            # В продакшені використовуємо Workload Identity
            self.client = firestore.Client(project=settings.PROJECT_ID)
        
        self.db = self.client.collection('bot_data')
        logger.info(f"Firestore клієнт ініціалізовано для середовища: {settings.ENVIRONMENT}")

    async def get_user(self, user_id: int):
        try:
            doc = self.db.document(f'users/{user_id}').get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            raise DatabaseError(f"Помилка отримання даних користувача: {str(e)}")

    async def save_user(self, user_id: int, data: dict):
        try:
            self.db.document(f'users/{user_id}').set(data)
        except Exception as e:
            raise DatabaseError(f"Помилка збереження даних користувача: {str(e)}")

    async def delete_user(self, user_id: int):
        try:
            self.db.document(f'users/{user_id}').delete()
        except Exception as e:
            raise DatabaseError(f"Помилка видалення даних користувача: {str(e)}")

# Створення глобального екземпляру клієнта
firestore_client = FirestoreClient() 