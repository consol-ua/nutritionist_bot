from google.cloud import firestore
from google.oauth2 import service_account
from ..core.config import get_settings
from ..core.exceptions import DatabaseError
import logging
import os
from typing import Optional, Dict, Any

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
        self.payments_collection = self.client.collection('payments')

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Отримує дані користувача"""
        try:
            doc = self.users_collection.document(str(user_id)).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            raise

    async def user_exists(self, user_id: int) -> bool:
        """Перевіряє чи існує користувач в базі даних"""
        try:
            doc = self.users_collection.document(str(user_id)).get()
            return doc.exists
        except Exception as e:
            raise DatabaseError(f"Error checking user existence: {str(e)}")

    async def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """Зберігає дані користувача"""
        try:
            self.users_collection.document(str(user_id)).set(user_data)
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")
            raise

    async def delete_user(self, user_id: int):
        try:
            self.users_collection.document(str(user_id)).delete()
        except Exception as e:
            raise DatabaseError(f"Error deleting user data: {str(e)}")

    async def save_job_id(self, user_id: int, job_id: Optional[str]):
        """Зберігає job_id для користувача"""
        try:
            self.users_collection.document(str(user_id)).update({
                'job_id': job_id,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            logger.error(f"Error saving job_id: {str(e)}")
            raise

    async def save_payment(self, user_id: int, invoice_id: str, status: str):
        """Зберігає дані про платіж"""
        try:
            payment_data = {
                'user_id': user_id,
                'invoice_id': invoice_id,
                'status': status,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            self.payments_collection.document(invoice_id).set(payment_data)
        except Exception as e:
            logger.error(f"Error saving payment data: {str(e)}")
            raise

    async def get_payment_by_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Отримує дані про платіж за invoice_id"""
        try:
            doc = self.payments_collection.document(invoice_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error getting payment data: {str(e)}")
            raise

    async def update_payment_status(self, invoice_id: str, status: str):
        """Оновлює статус платежу"""
        try:
            self.payments_collection.document(invoice_id).update({
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            raise

# Створення глобального екземпляру клієнта
firestore_client = FirestoreClient() 