"""
Payment and Wallet Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging

from .models import WalletBalance, WalletTransaction, PaymentTransaction
from .serializers import (
    WalletBalanceSerializer,
    WalletTransactionSerializer,
    PaymentTransactionSerializer,
    WalletTopUpRequestSerializer,
    PaymentCallbackSerializer,
    PaymentExecuteSerializer,
    PaymentQuerySerializer,
    RefundRequestSerializer
)
from .services import bkash_service

logger = logging.getLogger(__name__)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Wallet balance and transaction management
    
    list: Get user's wallet balance
    retrieve: Get wallet details
    transactions: Get wallet transaction history
    topup: Initiate wallet top-up with bKash
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = WalletBalanceSerializer
    
    def get_queryset(self):
        """User can only access their own wallet"""
        return WalletBalance.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get wallet transaction history"""
        wallet = self.get_object()
        transactions = wallet.transactions.all()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            transactions = transactions.filter(status=status_filter)
        
        # Filter by type
        type_filter = request.query_params.get('type')
        if type_filter:
            transactions = transactions.filter(transaction_type=type_filter)
        
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def topup(self, request, pk=None):
        """
        Initiate wallet top-up with bKash
        
        Request body:
        {
            "amount": 100.00,
            "payment_method": "bkash"
        }
        """
        wallet = self.get_object()
        serializer = WalletTopUpRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data['payment_method']
        
        # Create pending wallet transaction
        with transaction.atomic():
            wallet_transaction = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type=WalletTransaction.CREDIT,
                amount=amount,
                payment_method=payment_method,
                status=WalletTransaction.PENDING,
                description=f"Wallet top-up via {payment_method}",
                balance_after=wallet.balance
            )
            
            # Create bKash payment
            invoice_number = str(wallet_transaction.id)
            payment_result = bkash_service.create_payment(
                amount=amount,
                invoice_number=invoice_number
            )
            
            if payment_result.get('success'):
                # Update transaction with payment details
                wallet_transaction.gateway_transaction_id = payment_result.get('payment_id')
                wallet_transaction.gateway_response = payment_result.get('raw_response', {})
                wallet_transaction.save()
                
                return Response({
                    'success': True,
                    'transaction_id': str(wallet_transaction.id),
                    'payment_id': payment_result.get('payment_id'),
                    'bkash_url': payment_result.get('bkash_url'),
                    'amount': str(amount),
                    'message': 'Payment initiated. Please complete payment in bKash.'
                })
            else:
                # Mark transaction as failed
                wallet_transaction.status = WalletTransaction.FAILED
                wallet_transaction.gateway_response = payment_result
                wallet_transaction.save()
                
                return Response({
                    'success': False,
                    'error': payment_result.get('error', 'Failed to initiate payment')
                }, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Payment transaction management
    
    list: Get user's payment history
    retrieve: Get payment details
    execute: Execute bKash payment after user completes flow
    query: Query payment status
    refund: Request refund for a transaction
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionSerializer
    
    def get_queryset(self):
        """User can only access their own payments"""
        return PaymentTransaction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def execute(self, request):
        """
        Execute bKash payment after user completes payment flow
        
        Request body:
        {
            "payment_id": "TR00001234567890"
        }
        """
        serializer = PaymentExecuteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_id = serializer.validated_data['payment_id']
        
        # Find the wallet transaction
        try:
            wallet_transaction = WalletTransaction.objects.get(
                wallet__user=request.user,
                gateway_transaction_id=payment_id,
                status=WalletTransaction.PENDING
            )
        except WalletTransaction.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Transaction not found or already processed'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Execute payment with bKash
        execute_result = bkash_service.execute_payment(payment_id)
        
        if execute_result.get('success'):
            # Update wallet and transaction
            with transaction.atomic():
                wallet = wallet_transaction.wallet
                
                # Credit wallet
                wallet.credit(wallet_transaction.amount)
                
                # Update transaction
                wallet_transaction.status = WalletTransaction.COMPLETED
                wallet_transaction.balance_after = wallet.balance
                wallet_transaction.completed_at = timezone.now()
                wallet_transaction.gateway_response = execute_result.get('raw_response', {})
                wallet_transaction.save()
                
                logger.info(
                    f"Payment executed successfully: {payment_id} "
                    f"for user {request.user.email}"
                )
                
                return Response({
                    'success': True,
                    'transaction_id': str(wallet_transaction.id),
                    'trx_id': execute_result.get('trx_id'),
                    'amount': str(wallet_transaction.amount),
                    'new_balance': str(wallet.balance),
                    'message': 'Payment completed successfully'
                })
        else:
            # Mark as failed
            wallet_transaction.status = WalletTransaction.FAILED
            wallet_transaction.gateway_response = execute_result
            wallet_transaction.save()
            
            return Response({
                'success': False,
                'error': execute_result.get('error', 'Payment execution failed')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        Query payment status
        
        Request body:
        {
            "payment_id": "TR00001234567890"
        }
        """
        serializer = PaymentQuerySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_id = serializer.validated_data['payment_id']
        
        # Query payment from bKash
        query_result = bkash_service.query_payment(payment_id)
        
        if query_result.get('success'):
            return Response({
                'success': True,
                'payment_id': payment_id,
                'trx_id': query_result.get('trx_id'),
                'status': query_result.get('transaction_status'),
                'amount': query_result.get('amount')
            })
        else:
            return Response({
                'success': False,
                'error': query_result.get('error', 'Payment query failed')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def refund(self, request):
        """
        Request refund for a transaction
        Only admin users can process refunds
        
        Request body:
        {
            "transaction_id": "uuid",
            "reason": "Customer request"
        }
        """
        # Check if user has permission to refund
        if not request.user.is_staff:
            return Response({
                'error': 'Only admin users can process refunds'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RefundRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction_id = serializer.validated_data['transaction_id']
        reason = serializer.validated_data['reason']
        
        # Find the transaction
        try:
            wallet_transaction = WalletTransaction.objects.get(
                id=transaction_id,
                transaction_type=WalletTransaction.CREDIT,
                status=WalletTransaction.COMPLETED
            )
        except WalletTransaction.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Transaction not found or cannot be refunded'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get payment details from gateway_response
        gateway_response = wallet_transaction.gateway_response
        payment_id = wallet_transaction.gateway_transaction_id
        trx_id = gateway_response.get('trxID')
        
        if not trx_id:
            return Response({
                'success': False,
                'error': 'Transaction ID not found in gateway response'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process refund
        refund_result = bkash_service.refund_transaction(
            payment_id=payment_id,
            trx_id=trx_id,
            amount=wallet_transaction.amount,
            reason=reason
        )
        
        if refund_result.get('success'):
            # Update transaction and wallet
            with transaction.atomic():
                wallet = wallet_transaction.wallet
                
                # Debit wallet
                try:
                    wallet.debit(wallet_transaction.amount)
                except ValueError as e:
                    return Response({
                        'success': False,
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update transaction
                wallet_transaction.status = WalletTransaction.REFUNDED
                wallet_transaction.verified_by = request.user
                wallet_transaction.save()
                
                logger.info(
                    f"Refund processed: {trx_id} "
                    f"by {request.user.email}"
                )
                
                return Response({
                    'success': True,
                    'refund_trx_id': refund_result.get('refund_trx_id'),
                    'amount': str(wallet_transaction.amount),
                    'message': 'Refund processed successfully'
                })
        else:
            return Response({
                'success': False,
                'error': refund_result.get('error', 'Refund failed')
            }, status=status.HTTP_400_BAD_REQUEST)


@action(detail=False, methods=['post'], permission_classes=[])
def payment_callback(request):
    """
    bKash payment callback endpoint
    This is called by bKash after payment completion
    """
    serializer = PaymentCallbackSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"Invalid callback data: {request.data}")
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    payment_id = serializer.validated_data['payment_id']
    payment_status = serializer.validated_data['status']
    
    logger.info(f"Payment callback received: {payment_id} - {payment_status}")
    
    # Find the transaction and update status
    try:
        wallet_transaction = WalletTransaction.objects.get(
            gateway_transaction_id=payment_id
        )
        
        # Store callback response
        wallet_transaction.gateway_response.update({
            'callback_status': payment_status,
            'callback_time': timezone.now().isoformat()
        })
        wallet_transaction.save()
        
        return Response({
            'success': True,
            'message': 'Callback processed'
        })
        
    except WalletTransaction.DoesNotExist:
        logger.error(f"Transaction not found for payment_id: {payment_id}")
        return Response({
            'success': False,
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
