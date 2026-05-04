from typing import Optional
import aiohttp
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MonobankPayment(BaseModel):
    amount: int
    redirect_url: str
    webhook_url: Optional[str] = None

class MonobankService:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.monobank.ua/api"
        self.headers = {
            "X-Token": self.api_token,
            "Content-Type": "application/json"
        }

    async def create_payment(self, payment: MonobankPayment) -> dict:
        """
        Створює новий платіж через Monobank API
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/merchant/invoice/create"
            payload = {
                "amount": payment.amount,
                "redirectUrl": payment.redirect_url,
                "webhookUrl": payment.webhook_url
            }
            
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f'Error create_payment {error_text}')
                    return await response.json()

    async def remove_payment(self, invoice_id: str) -> dict:
        """
        Видаляє платеж
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/merchant/invoice/remove"
            payload = {"invoiceId": invoice_id}

            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f'Error remove_payment {error_text}')
                    return await response.json()

    async def check_payment_status(self, invoice_id: str) -> dict:
        """
        Перевіряє статус платежу
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/merchant/invoice/status"
            params = {"invoiceId": invoice_id}
            
            async with session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f'Error check_payment_status {error_text}')
                    return await response.json()