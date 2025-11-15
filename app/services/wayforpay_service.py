from typing import Optional, List
import aiohttp
import hashlib
import time
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WayForPayPayment(BaseModel):
    order_reference: str
    amount: float
    currency: str = "UAH"
    product_name: List[str]
    product_count: List[int]
    product_price: List[float]
    return_url: str
    service_url: Optional[str] = None
    order_date: Optional[int] = None


class WayForPayService:
    def __init__(self, merchant_account: str, merchant_secret_key: str, merchant_domain_name: str):
        self.merchant_account = merchant_account
        self.merchant_secret_key = merchant_secret_key
        self.merchant_domain_name = merchant_domain_name
        self.base_url = "https://secure.wayforpay.com"

    def _generate_signature(self, order_reference: str, order_date: int, amount: float, 
                           currency: str, product_name: List[str], product_count: List[int], 
                           product_price: List[float]) -> str:
        """
        Генерує підпис для запиту WayForPay
        """
        signature_str = ';'.join([
            self.merchant_account,
            self.merchant_secret_key,
            order_reference,
            str(order_date),
            str(amount),
            currency,
            ';'.join(product_name),
            ';'.join(map(str, product_count)),
            ';'.join(map(str, product_price))
        ])
        return hashlib.md5(signature_str.encode('utf-8')).hexdigest()

    async def create_payment(self, payment: WayForPayPayment) -> dict:
        """
        Створює новий платіж через WayForPay API
        """
        order_date = payment.order_date or int(time.time())
        
        signature = self._generate_signature(
            payment.order_reference,
            order_date,
            payment.amount,
            payment.currency,
            payment.product_name,
            payment.product_count,
            payment.product_price
        )
        
        payload = {
            'merchantAccount': self.merchant_account,
            'merchantAuthType': 'SimpleSignature',
            'merchantDomainName': self.merchant_domain_name,
            'orderReference': payment.order_reference,
            'orderDate': order_date,
            'amount': payment.amount,
            'currency': payment.currency,
            'productName': payment.product_name,
            'productCount': payment.product_count,
            'productPrice': payment.product_price,
            'merchantSignature': signature,
            'returnUrl': payment.return_url,
        }
        
        if payment.service_url:
            payload['serviceUrl'] = payment.service_url
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pay"
            
            try:
                async with session.post(url, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        if response_data.get('reasonCode') == 1100:
                            logger.info(f"Payment created successfully: {payment.order_reference}")
                            return response_data
                        else:
                            error_reason = response_data.get('reason', 'Unknown error')
                            logger.error(f'Error create_payment: {error_reason}')
                            return response_data
                    else:
                        error_text = await response.text()
                        logger.error(f'Error create_payment HTTP {response.status}: {error_text}')
                        return {'error': error_text, 'status': response.status}
            except Exception as e:
                logger.error(f'Exception in create_payment: {str(e)}')
                raise

    async def check_payment_status(self, order_reference: str) -> dict:
        """
        Перевіряє статус платежу через WayForPay API
        """
        order_date = int(time.time())
        
        # Формуємо підпис для запиту статусу
        signature_str = ';'.join([
            self.merchant_account,
            self.merchant_secret_key,
            order_reference
        ])
        signature = hashlib.md5(signature_str.encode('utf-8')).hexdigest()
        
        payload = {
            'merchantAccount': self.merchant_account,
            'orderReference': order_reference,
            'merchantSignature': signature
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api"
            
            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f'Error check_payment_status HTTP {response.status}: {error_text}')
                        return {'error': error_text, 'status': response.status}
            except Exception as e:
                logger.error(f'Exception in check_payment_status: {str(e)}')
                raise

    def verify_webhook_signature(self, data: dict) -> bool:
        """
        Перевіряє підпис вебхука від WayForPay
        Для вебхуків підпис формується з merchantSecretKey
        """
        try:
            order_reference = data.get('orderReference', '')
            status = data.get('transactionStatus', '') or data.get('status', '')
            time = data.get('time', '')
            received_signature = data.get('merchantSignature', '')
            
            if not received_signature:
                logger.warning("No signature in webhook data")
                return False
            
            # Формуємо підпис для перевірки (з merchantSecretKey)
            signature_str = ';'.join([
                order_reference,
                status,
                str(time)
            ])
            signature_with_key = signature_str + ';' + self.merchant_secret_key
            calculated_signature = hashlib.md5(signature_with_key.encode('utf-8')).hexdigest()
            
            return calculated_signature == received_signature
        except Exception as e:
            logger.error(f'Error verifying webhook signature: {str(e)}')
            return False
