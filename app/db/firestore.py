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
            
        elif settings.ENVIRONMENT == "production":
            # В продакшені використовуємо Workload Identity
            self.client = firestore.Client(project=settings.PROJECT_ID)
            
        else:
            raise DatabaseError(f"Unknown environment: {settings.ENVIRONMENT}")
        
        # Ініціалізуємо колекції
        self.users_collection = self.client.collection('users')
        self.payments_collection = self.client.collection('payments')

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Отримує дані користувача з бази даних"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            raise DatabaseError(f"Error getting user data: {str(e)}")

    async def save_user(self, user_id: int, user_data: Dict[str, Any]) -> None:
        """Зберігає дані користувача в базу даних"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            doc_ref.set(user_data)
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")
            raise DatabaseError(f"Error saving user data: {str(e)}")

    async def user_has_access(self, user_id: int) -> bool:
        """Перевіряє чи має користувач доступ до контенту"""
        try:
            user = await self.get_user(user_id)
            return user.get('access', False) if user else False
        except Exception as e:
            logger.error(f"Error checking user access: {str(e)}")
            return False

    async def save_job_id(self, user_id: int, job_id: Optional[str]) -> None:
        """Зберігає job_id для користувача"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            doc_ref.update({'job_id': job_id})
        except Exception as e:
            logger.error(f"Error saving job_id: {str(e)}")
            raise DatabaseError(f"Error saving job_id: {str(e)}")

    async def save_payment(self, user_id: int, invoice_id: str, status: str, payment_url: str) -> None:
        """Зберігає дані платежу"""
        try:
            payment_data = {
                'user_id': user_id,
                'invoice_id': invoice_id,
                'status': status,
                'payment_url': payment_url,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            doc_ref = self.payments_collection.document(invoice_id)
            doc_ref.set(payment_data)
        except Exception as e:
            logger.error(f"Error saving payment data: {str(e)}")
            raise DatabaseError(f"Error saving payment data: {str(e)}")

    async def get_payment_by_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Отримує платіж користувача"""
        try:
            query = self.payments_collection.where('user_id', '==', user_id).limit(1)
            docs = query.stream()
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting payment data: {str(e)}")
            raise DatabaseError(f"Error getting payment data: {str(e)}")

    async def get_payment_by_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Отримує платіж за invoice_id"""
        try:
            doc_ref = self.payments_collection.document(invoice_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting payment data: {str(e)}")
            raise DatabaseError(f"Error getting payment data: {str(e)}")

    async def update_payment_status(self, invoice_id: str, status: str) -> None:
        """Оновлює статус платежу"""
        try:
            doc_ref = self.payments_collection.document(invoice_id)
            doc_ref.update({'status': status})
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            raise DatabaseError(f"Error updating payment status: {str(e)}")

    async def update_user_access(self, user_id: int) -> None:
        """Оновлює доступ користувача"""
        try:
            doc_ref = self.users_collection.document(str(user_id))
            doc_ref.update({
                'access': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            logger.error(f"Error updating user access: {str(e)}")
            raise DatabaseError(f"Error updating user access: {str(e)}")

# Створюємо глобальний екземпляр клієнта
firestore_client = FirestoreClient() 