"""
bKash Payment Gateway Integration Service
Official bKash Tokenized Checkout API
"""

import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class BkashPaymentService:
    """
    bKash Payment Gateway Service
    Handles payment creation, execution, query, and refund
    """
    
    # bKash API URLs
    SANDBOX_BASE_URL = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"
    PRODUCTION_BASE_URL = "https://tokenized.pay.bka.sh/v1.2.0-beta"
    
    def __init__(self):
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.base_url = (
            self.SANDBOX_BASE_URL 
            if settings.BKASH_SANDBOX 
            else self.PRODUCTION_BASE_URL
        )
        self.token = None
        self.token_expiry = None
    
    def get_headers(self, with_auth=False):
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-APP-Key': self.app_key,
        }
        
        if with_auth and self.token:
            headers['Authorization'] = self.token
        
        return headers
    
    def grant_token(self):
        """
        Get authorization token from bKash
        Token is valid for 1 hour
        """
        try:
            url = f"{self.base_url}/tokenized/checkout/token/grant"
            
            payload = {
                "app_key": self.app_key,
                "app_secret": self.app_secret
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('id_token')
                self.token_expiry = timezone.now() + timezone.timedelta(minutes=50)
                logger.info("bKash token granted successfully")
                return True
            else:
                logger.error(f"Failed to grant bKash token: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error granting bKash token: {str(e)}")
            return False
    
    def refresh_token(self):
        """
        Refresh authorization token
        Should be called before token expires
        """
        try:
            url = f"{self.base_url}/tokenized/checkout/token/refresh"
            
            payload = {
                "app_key": self.app_key,
                "app_secret": self.app_secret,
                "refresh_token": self.token
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('id_token')
                self.token_expiry = timezone.now() + timezone.timedelta(minutes=50)
                logger.info("bKash token refreshed successfully")
                return True
            else:
                logger.error(f"Failed to refresh bKash token: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing bKash token: {str(e)}")
            return False
    
    def ensure_token(self):
        """Ensure we have a valid token"""
        if not self.token or (self.token_expiry and timezone.now() >= self.token_expiry):
            return self.grant_token()
        return True
    
    def create_payment(self, amount, invoice_number, merchant_invoice_number=None):
        """
        Create a payment request
        
        Args:
            amount: Payment amount (Decimal or float)
            invoice_number: Unique invoice number from your system
            merchant_invoice_number: Optional merchant invoice number
        
        Returns:
            dict: Payment creation response with paymentID and bkashURL
        """
        try:
            if not self.ensure_token():
                return {
                    'success': False,
                    'error': 'Failed to obtain authorization token'
                }
            
            url = f"{self.base_url}/tokenized/checkout/create"
            
            # Convert amount to string with 2 decimal places
            amount_str = f"{Decimal(str(amount)):.2f}"
            
            payload = {
                "mode": "0011",  # Instant Checkout
                "payerReference": " ",
                "callbackURL": settings.BKASH_CALLBACK_URL,
                "amount": amount_str,
                "currency": "BDT",
                "intent": "sale",
                "merchantInvoiceNumber": merchant_invoice_number or invoice_number
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(with_auth=True)
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('statusCode') == '0000':
                logger.info(f"Payment created successfully: {data.get('paymentID')}")
                return {
                    'success': True,
                    'payment_id': data.get('paymentID'),
                    'bkash_url': data.get('bkashURL'),
                    'callback_url': data.get('callbackURL'),
                    'amount': amount_str,
                    'invoice_number': invoice_number,
                    'raw_response': data
                }
            else:
                logger.error(f"Failed to create payment: {data}")
                return {
                    'success': False,
                    'error': data.get('statusMessage', 'Payment creation failed'),
                    'raw_response': data
                }
                
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_payment(self, payment_id):
        """
        Execute a payment after user completes bKash flow
        
        Args:
            payment_id: Payment ID from create_payment response
        
        Returns:
            dict: Payment execution response
        """
        try:
            if not self.ensure_token():
                return {
                    'success': False,
                    'error': 'Failed to obtain authorization token'
                }
            
            url = f"{self.base_url}/tokenized/checkout/execute"
            
            payload = {
                "paymentID": payment_id
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(with_auth=True)
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('statusCode') == '0000':
                logger.info(f"Payment executed successfully: {payment_id}")
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'trx_id': data.get('trxID'),
                    'transaction_status': data.get('transactionStatus'),
                    'amount': data.get('amount'),
                    'customer_msisdn': data.get('customerMsisdn'),
                    'raw_response': data
                }
            else:
                logger.error(f"Failed to execute payment: {data}")
                return {
                    'success': False,
                    'error': data.get('statusMessage', 'Payment execution failed'),
                    'raw_response': data
                }
                
        except Exception as e:
            logger.error(f"Error executing payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_payment(self, payment_id):
        """
        Query payment status
        
        Args:
            payment_id: Payment ID to query
        
        Returns:
            dict: Payment status information
        """
        try:
            if not self.ensure_token():
                return {
                    'success': False,
                    'error': 'Failed to obtain authorization token'
                }
            
            url = f"{self.base_url}/tokenized/checkout/payment/status"
            
            payload = {
                "paymentID": payment_id
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(with_auth=True)
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'trx_id': data.get('trxID'),
                    'transaction_status': data.get('transactionStatus'),
                    'amount': data.get('amount'),
                    'raw_response': data
                }
            else:
                logger.error(f"Failed to query payment: {data}")
                return {
                    'success': False,
                    'error': data.get('statusMessage', 'Payment query failed'),
                    'raw_response': data
                }
                
        except Exception as e:
            logger.error(f"Error querying payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_transaction(self, trx_id):
        """
        Search transaction by trxID
        
        Args:
            trx_id: bKash transaction ID
        
        Returns:
            dict: Transaction information
        """
        try:
            if not self.ensure_token():
                return {
                    'success': False,
                    'error': 'Failed to obtain authorization token'
                }
            
            url = f"{self.base_url}/tokenized/checkout/general/searchTransaction"
            
            payload = {
                "trxID": trx_id
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(with_auth=True)
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'trx_id': trx_id,
                    'raw_response': data
                }
            else:
                return {
                    'success': False,
                    'error': data.get('statusMessage', 'Transaction search failed'),
                    'raw_response': data
                }
                
        except Exception as e:
            logger.error(f"Error searching transaction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_transaction(self, payment_id, trx_id, amount, reason="Customer Request"):
        """
        Refund a transaction
        
        Args:
            payment_id: Original payment ID
            trx_id: Transaction ID to refund
            amount: Amount to refund
            reason: Refund reason
        
        Returns:
            dict: Refund response
        """
        try:
            if not self.ensure_token():
                return {
                    'success': False,
                    'error': 'Failed to obtain authorization token'
                }
            
            url = f"{self.base_url}/tokenized/checkout/payment/refund"
            
            amount_str = f"{Decimal(str(amount)):.2f}"
            
            payload = {
                "paymentID": payment_id,
                "trxID": trx_id,
                "amount": amount_str,
                "reason": reason,
                "sku": "payment"
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(with_auth=True)
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('statusCode') == '0000':
                logger.info(f"Refund successful: {trx_id}")
                return {
                    'success': True,
                    'refund_trx_id': data.get('refundTrxID'),
                    'transaction_status': data.get('transactionStatus'),
                    'raw_response': data
                }
            else:
                logger.error(f"Failed to refund: {data}")
                return {
                    'success': False,
                    'error': data.get('statusMessage', 'Refund failed'),
                    'raw_response': data
                }
                
        except Exception as e:
            logger.error(f"Error refunding transaction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
bkash_service = BkashPaymentService()
