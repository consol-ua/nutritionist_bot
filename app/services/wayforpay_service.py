from typing import Optional, List
import aiohttp
import hashlib
import hmac
import time
from pydantic import BaseModel
from datetime import datetime
import logging
from urllib.parse import urlencode
import json
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WayForPayPayment(BaseModel):
    order_reference: str
    amount: float
    currency: str = "UAH"
    product_name: List[str]
    product_count: List[int]
    product_price: List[float]
    service_url: Optional[str] = None
    order_date: Optional[int] = None


class WayForPayService:
    def __init__(self, merchant_account: str, merchant_secret_key: str, merchant_domain_name: str):
        self.merchant_account = merchant_account
        self.merchant_secret_key = merchant_secret_key
        self.merchant_domain_name = merchant_domain_name
        self.base_url = "https://api.wayforpay.com"
        self.secure_url = "https://secure.wayforpay.com"

    def _generate_signature(self, order_reference: str, order_date: int, amount: float, 
                           currency: str, product_name: List[str], product_count: List[int], 
                           product_price: List[float], use_domain_name: bool = True) -> str:
        """
        Генерує HMAC-MD5 підпис для запиту WayForPay
        
        Рядок формується з: merchantAccount, [merchantDomainName], orderReference, 
        orderDate, amount, currency, productName[0], ..., productName[n], 
        productCount[0], ..., productCount[n], productPrice[0], ..., productPrice[n]
        розділених ";" в кодуванні UTF-8
        
        Примітка: amount та productPrice мають бути відформатовані як числа з 2 знаками після коми
        """
        # Форматуємо amount та productPrice - WayForPay очікує формат з 2 знаками після коми
        # Завжди використовуємо формат "XXX.XX" (наприклад: 340.00, 340.50, 340.55)
        amount_str = f"{amount:.2f}"
        product_price_str = [f"{p:.2f}" for p in product_price]
        
        # Формуємо рядок для підпису згідно з документацією WayForPay
        signature_parts = [self.merchant_account]
        
        # merchantDomainName може не потрібен для API запитів
        if use_domain_name:
            signature_parts.append(self.merchant_domain_name)
        
        signature_parts.extend([
            order_reference,
            str(order_date),
            amount_str,
            currency
        ])
        
        # Додаємо кожен productName окремо
        signature_parts.extend(product_name)
        
        # Додаємо кожен productCount окремо (як рядки)
        signature_parts.extend(map(str, product_count))
        
        # Додаємо кожен productPrice окремо
        signature_parts.extend(product_price_str)
        
        # Об'єднуємо всі частини через ";"
        signature_str = ';'.join(signature_parts)
        
        # Логуємо рядок для підпису (без secret key) для діагностики
        logger.info(f"WayForPay signature string (without key, use_domain={use_domain_name}): {signature_str}")
        
        # Генеруємо HMAC-MD5 підпис з використанням SecretKey
        signature_bytes = hmac.new(
            self.merchant_secret_key.encode('utf-8'),
            signature_str.encode('utf-8'),
            hashlib.md5
        ).hexdigest()
        
        logger.info(f"WayForPay generated signature: {signature_bytes}")
        
        return signature_bytes

    async def create_payment(self, payment: WayForPayPayment) -> dict:
        """
        Створює новий платіж через WayForPay API
        """
        order_date = payment.order_date or int(time.time())
        
        # Для API запитів CREATE_INVOICE спробуємо спочатку з merchantDomainName
        # Якщо не спрацює (помилка 1113), спробуємо без merchantDomainName
        use_domain_name = True  # Спочатку пробуємо з domain_name
        signature = self._generate_signature(
            payment.order_reference,
            order_date,
            payment.amount,
            payment.currency,
            payment.product_name,
            payment.product_count,
            payment.product_price,
            use_domain_name=use_domain_name
        )
        
        # Форматуємо amount та productPrice - WayForPay може очікувати однаковий формат в payload та підписі
        # Використовуємо рядки з форматом "340.00" для узгодженості з підписом
        amount_formatted = f"{payment.amount:.2f}"
        product_price_formatted = [f"{p:.2f}" for p in payment.product_price]
        # returnUrl = f"https://t.me/{settings.BOT_USERNAME}"
        
        payload = {
            'apiVersion': 1,
            'transactionType': 'CREATE_INVOICE',
            'merchantAccount': self.merchant_account,
            'merchantAuthType': 'SimpleSignature',
            'merchantDomainName': self.merchant_domain_name,
            'orderReference': payment.order_reference,
            'orderDate': order_date,
            'amount': amount_formatted,  # Використовуємо рядок для узгодженості з підписом
            'currency': payment.currency,
            'productName': payment.product_name,
            'productCount': payment.product_count,
            'productPrice': product_price_formatted,  # Використовуємо рядки для узгодженості з підписом
            'merchantSignature': signature
            # 'returnUrl': returnUrl
        }
        
        if payment.service_url:
            payload['serviceUrl'] = payment.service_url
        
        async with aiohttp.ClientSession() as session:
            # WayForPay API використовує /api для створення інвойсу
            url = f"{self.base_url}/api"
            
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Логуємо повний запит з параметрами
                logger.info(f"WayForPay create_payment request:")
                logger.info(f"  URL: {url}")
                logger.info(f"  Headers: {json.dumps(headers, indent=2, ensure_ascii=False)}")
                logger.info(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                
                async with session.post(url, json=payload, headers=headers) as response:
                    # Перевіряємо Content-Type перед спробою парсити JSON
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if 'application/json' not in content_type:
                        # Якщо сервер повертає HTML, читаємо текст і логуємо
                        response_text = await response.text()
                        logger.error(f'WayForPay API returned HTML instead of JSON. Status: {response.status}, Content-Type: {content_type}, Response preview: {response_text[:500]}')
                        return {
                            'error': 'WayForPay API returned HTML instead of JSON',
                            'status': response.status,
                            'content_type': content_type,
                            'response_preview': response_text[:500]
                        }
                    
                    try:
                        response_data = await response.json()
                    except aiohttp.ContentTypeError as e:
                        # Якщо не вдалося розпарсити JSON, читаємо текст
                        response_text = await response.text()
                        logger.error(f'Failed to parse JSON response: {str(e)}, Response: {response_text[:500]}')
                        return {
                            'error': f'Failed to parse JSON: {str(e)}',
                            'status': response.status,
                            'response_preview': response_text[:500]
                        }
                    
                    if response.status == 200:
                        # Якщо помилка з підписом, спробуємо без merchantDomainName
                        if response_data.get('reasonCode') == 1113 and use_domain_name:
                            logger.warning("Invalid signature with domain name, trying without domain name")
                            signature = self._generate_signature(
                                payment.order_reference,
                                order_date,
                                payment.amount,
                                payment.currency,
                                payment.product_name,
                                payment.product_count,
                                payment.product_price,
                                use_domain_name=False
                            )
                            payload['merchantSignature'] = signature
                            # Повторюємо запит з новим підписом
                            async with session.post(url, json=payload, headers=headers) as retry_response:
                                if retry_response.status == 200:
                                    response_data = await retry_response.json()
                        
                        if response_data.get('reasonCode') == 1100:
                            # WayForPay повертає invoiceUrl для переходу на форму оплати
                            invoice_url = response_data.get('invoiceUrl')
                            if invoice_url:
                                logger.info(f"Payment created successfully: {payment.order_reference}")
                                return response_data
                            else:
                                # Якщо немає invoiceUrl, створюємо URL для форми оплати
                                url_params = {}
                                for k, v in payload.items():
                                    if isinstance(v, list):
                                        url_params[k] = ';'.join(map(str, v))
                                    else:
                                        url_params[k] = str(v)
                                payment_url = f"{self.secure_url}/pay?" + urlencode(url_params)
                                response_data['invoiceUrl'] = payment_url
                                logger.info(f"Payment form URL created: {payment.order_reference}")
                                return response_data
                        else:
                            error_reason = response_data.get('reason', 'Unknown error')
                            logger.error(f'Error create_payment: {error_reason}')
                            return response_data
                    else:
                        error_text = await response.text()
                        logger.error(f'Error create_payment HTTP {response.status}: {error_text[:500]}')
                        return {'error': error_text[:500], 'status': response.status}
            except Exception as e:
                logger.error(f'Exception in create_payment: {str(e)}', exc_info=True)
                raise

    async def check_payment_status(self, order_reference: str) -> dict:
        """
        Перевіряє статус платежу через WayForPay API
        """
        # Формуємо підпис для запиту статусу
        # Для CHECK_STATUS підпис формується з merchantAccount та orderReference
        signature_str = ';'.join([
            self.merchant_account,
            order_reference
        ])
        # Генеруємо HMAC-MD5 підпис
        signature = hmac.new(
            self.merchant_secret_key.encode('utf-8'),
            signature_str.encode('utf-8'),
            hashlib.md5
        ).hexdigest()
        
        payload = {
            'transactionType': 'CHECK_STATUS',
            'merchantAccount': self.merchant_account,
            'orderReference': order_reference,
            'merchantSignature': signature
        }
        
        async with aiohttp.ClientSession() as session:
            # WayForPay може не мати окремого API ендпоінту для перевірки статусу
            # Статус перевіряється через вебхуки або через merchant panel
            # Спробуємо використати /api, але якщо не працює, повернемо помилку
            url = f"{self.base_url}/api"
            
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Логуємо повний запит з параметрами
                logger.info(f"WayForPay check_payment_status request:")
                logger.info(f"  URL: {url}")
                logger.info(f"  Headers: {json.dumps(headers, indent=2, ensure_ascii=False)}")
                logger.info(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                
                async with session.post(url, json=payload, headers=headers) as response:
                    # Якщо ендпоінт не існує (404), повертаємо помилку
                    if response.status == 404:
                        logger.warning(f'WayForPay API endpoint /api not found. Status checking may not be available via API.')
                        return {
                            'error': 'WayForPay API endpoint not found. Status should be checked via webhooks.',
                            'status': 404
                        }
                    
                    # Перевіряємо Content-Type перед спробою парсити JSON
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if 'application/json' not in content_type:
                        response_text = await response.text()
                        logger.error(f'WayForPay API returned HTML instead of JSON. Status: {response.status}, Content-Type: {content_type}, Response preview: {response_text[:500]}')
                        return {
                            'error': 'WayForPay API returned HTML instead of JSON',
                            'status': response.status,
                            'content_type': content_type
                        }
                    
                    try:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logger.error(f'Error check_payment_status HTTP {response.status}: {error_text}')
                            return {'error': error_text, 'status': response.status}
                    except aiohttp.ContentTypeError as e:
                        response_text = await response.text()
                        logger.error(f'Failed to parse JSON response: {str(e)}, Response: {response_text[:500]}')
                        return {
                            'error': f'Failed to parse JSON: {str(e)}',
                            'status': response.status
                        }
            except Exception as e:
                logger.error(f'Exception in check_payment_status: {str(e)}', exc_info=True)
                raise

    def generate_wayforpay_webhook_response_signature(self,order_reference: str, status: str, time_value: int) -> str:
        string_to_sign = f"{order_reference};{status};{time_value}"
        signature = hmac.new(
            self.merchant_secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.md5
        ).hexdigest()
        return signature


