from google.cloud import firestore
from google.oauth2 import service_account
from ..core.config import get_settings
from ..core.exceptions import DatabaseError
import logging
import os

logger = logging.getLogger(__name__)
settings = get_settings()

class FirestoreClient:
    def __init__(self):
        if settings.ENVIRONMENT == "development":
            # В режимі розробки використовуємо service account файл
            credentials = settings.get_google_credentials()
            if not credentials or not credentials.get("credentials_file"):
                raise DatabaseError("Не знайдено файл credentials для development середовища")
            
            credentials = service_account.Credentials.from_service_account_file(
                credentials["credentials_file"]
            )
            self.client = firestore.Client(
                project=settings.PROJECT_ID,
                credentials=credentials
            )
            logger.info("Firestore client initialized for development environment")
            
        elif settings.ENVIRONMENT == "production":
            # В продакшені використовуємо Workload Identity
            self.client = firestore.Client(project=settings.PROJECT_ID)
            logger.info("Firestore client initialized for production environment")
            
        else:
            raise DatabaseError(f"Unknown environment: {settings.ENVIRONMENT}")
        
        # Ініціалізуємо колекції
        self.users_collection = self.client.collection('users')

    async def get_user(self, user_id: int):
        try:
            doc = self.users_collection.document(str(user_id)).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            raise DatabaseError(f"Error getting user data: {str(e)}")

    async def user_exists(self, user_id: int) -> bool:
        """Перевіряє чи існує користувач в базі даних"""
        try:
            doc = self.users_collection.document(str(user_id)).get()
            return doc.exists
        except Exception as e:
            raise DatabaseError(f"Error checking user existence: {str(e)}")

    async def save_user(self, user_id: int, data: dict):
        try:
            self.users_collection.document(str(user_id)).set(data)
        except Exception as e:
            raise DatabaseError(f"Error saving user data: {str(e)}")

    async def delete_user(self, user_id: int):
        try:
            self.users_collection.document(str(user_id)).delete()
        except Exception as e:
            raise DatabaseError(f"Error deleting user data: {str(e)}")

    async def save_job_id(self, user_id: int, job_id: str):
        """Зберігає job_id для користувача"""
        try:
            user_ref = self.users_collection.document(str(user_id))
            user_ref.update({
                'job_id': job_id,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            logger.info(f"Saved job_id {job_id} for user {user_id}")
        except Exception as e:
            raise DatabaseError(f"Error saving job_id: {str(e)}")

# Створення глобального екземпляру клієнта
firestore_client = FirestoreClient() 