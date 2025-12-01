from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class WalletBalance(models.Model):
    """User's wallet balance for PDF export payments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    
    # Balance in BDT (Bangladeshi Taka)
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current wallet balance in BDT"
    )
    
    # Lifetime statistics
    total_credited = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount ever credited"
    )
    total_debited = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount ever spent"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Wallet Balance'
        verbose_name_plural = 'Wallet Balances'
    
    def __str__(self):
        return f"{self.user.email} - {self.balance} BDT"
    
    def credit(self, amount, description=""):
        """Add money to wallet"""
        self.balance += amount
        self.total_credited += amount
        self.save()
        return self.balance
    
    def debit(self, amount, description=""):
        """Deduct money from wallet"""
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.total_debited += amount
        self.save()
        return self.balance
    
    def has_sufficient_balance(self, amount):
        """Check if user has enough balance"""
        return self.balance >= amount


class WalletTransaction(models.Model):
    """Wallet top-up and deduction history"""
    
    # Transaction Types
    CREDIT = 'credit'
    DEBIT = 'debit'
    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, 'Credit (Top-up)'),
        (DEBIT, 'Debit (Spent)'),
    ]
    
    # Payment Methods
    BKASH = 'bkash'
    NAGAD = 'nagad'
    ROCKET = 'rocket'
    BANK = 'bank'
    PAYMENT_METHOD_CHOICES = [
        (BKASH, 'bKash'),
        (NAGAD, 'Nagad'),
        (ROCKET, 'Rocket'),
        (BANK, 'Bank Transfer'),
    ]
    
    # Transaction Status
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        WalletBalance,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction details
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # For credit transactions
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    
    # Payment gateway references
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Transaction status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    
    # Description
    description = models.TextField(blank=True)
    
    # Balance after transaction
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Admin actions
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_transactions'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        indexes = [
            models.Index(fields=['wallet', 'transaction_type']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type.upper()} - {self.amount} BDT - {self.status}"


class PaymentTransaction(models.Model):
    """PDF export payment records"""
    
    # Payment Status
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    wallet = models.ForeignKey(
        WalletBalance,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount deducted for PDF export"
    )
    
    # What was purchased
    mcq_count = models.PositiveIntegerField(default=0)
    cq_count = models.PositiveIntegerField(default=0)
    
    # Pricing breakdown
    mcq_price_per_question = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.50')
    )
    cq_price_per_question = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('3.00')
    )
    
    # PDF reference
    draft = models.ForeignKey(
        'questions.UserDraft',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    pdf_file = models.FileField(
        upload_to='exports/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Transaction status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=COMPLETED
    )
    
    # Balance after payment
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Related wallet transaction
    wallet_transaction = models.OneToOneField(
        WalletTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} BDT - {self.status}"
    
    @property
    def total_questions(self):
        return self.mcq_count + self.cq_count
