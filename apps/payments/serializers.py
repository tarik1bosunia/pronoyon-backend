"""
Payment and Wallet Serializers
"""

from rest_framework import serializers
from decimal import Decimal
from .models import WalletBalance, WalletTransaction, PaymentTransaction


class WalletBalanceSerializer(serializers.ModelSerializer):
    """Serializer for wallet balance"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WalletBalance
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'balance',
            'total_credited',
            'total_debited',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'balance',
            'total_credited',
            'total_debited',
            'created_at',
            'updated_at'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for wallet transactions"""
    
    user_email = serializers.EmailField(source='wallet.user.email', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id',
            'wallet',
            'user_email',
            'transaction_type',
            'amount',
            'payment_method',
            'payment_method_display',
            'gateway_transaction_id',
            'gateway_response',
            'status',
            'status_display',
            'description',
            'balance_after',
            'verified_by',
            'created_at',
            'completed_at'
        ]
        read_only_fields = [
            'id',
            'balance_after',
            'created_at',
            'completed_at'
        ]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id',
            'user',
            'user_email',
            'wallet',
            'amount',
            'mcq_count',
            'cq_count',
            'total_questions',
            'mcq_price_per_question',
            'cq_price_per_question',
            'draft',
            'pdf_file',
            'status',
            'status_display',
            'balance_after',
            'wallet_transaction',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'balance_after',
            'wallet_transaction',
            'created_at'
        ]


class WalletTopUpRequestSerializer(serializers.Serializer):
    """Serializer for wallet top-up request"""
    
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('10.00'),
        max_value=Decimal('50000.00'),
        help_text="Amount to add to wallet (10 - 50000 BDT)"
    )
    payment_method = serializers.ChoiceField(
        choices=WalletTransaction.PAYMENT_METHOD_CHOICES,
        default=WalletTransaction.BKASH
    )


class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for bKash payment callback"""
    
    payment_id = serializers.CharField(
        max_length=200,
        help_text="bKash payment ID"
    )
    status = serializers.CharField(
        max_length=50,
        help_text="Payment status from bKash"
    )


class PaymentExecuteSerializer(serializers.Serializer):
    """Serializer for payment execution"""
    
    payment_id = serializers.CharField(
        max_length=200,
        help_text="bKash payment ID to execute"
    )


class PaymentQuerySerializer(serializers.Serializer):
    """Serializer for payment query"""
    
    payment_id = serializers.CharField(
        max_length=200,
        help_text="bKash payment ID to query"
    )


class RefundRequestSerializer(serializers.Serializer):
    """Serializer for refund request"""
    
    transaction_id = serializers.UUIDField(
        help_text="Wallet transaction ID to refund"
    )
    reason = serializers.CharField(
        max_length=500,
        default="Customer Request",
        help_text="Reason for refund"
    )
