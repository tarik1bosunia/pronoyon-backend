from django.contrib import admin
from django.utils.html import format_html
from .models import WalletBalance, WalletTransaction, PaymentTransaction


@admin.register(WalletBalance)
class WalletBalanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_email', 'balance_display', 'total_credited_display', 
        'total_debited_display', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'id', 'balance', 'total_credited', 'total_debited', 
        'created_at', 'updated_at'
    ]
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def balance_display(self, obj):
        color = 'green' if obj.balance > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">৳{}</span>',
            color, obj.balance
        )
    balance_display.short_description = 'Balance'
    balance_display.admin_order_field = 'balance'
    
    def total_credited_display(self, obj):
        return format_html(
            '<span style="color: green;">৳{}</span>',
            obj.total_credited
        )
    total_credited_display.short_description = 'Total Credited'
    
    def total_debited_display(self, obj):
        return format_html(
            '<span style="color: red;">৳{}</span>',
            obj.total_debited
        )
    total_debited_display.short_description = 'Total Debited'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_email', 'transaction_type', 'amount_display', 
        'payment_method', 'status_badge', 'balance_after_display', 'created_at'
    ]
    list_filter = [
        'transaction_type', 'payment_method', 'status', 'created_at'
    ]
    search_fields = [
        'wallet__user__email', 'gateway_transaction_id', 'description'
    ]
    readonly_fields = [
        'id', 'wallet', 'transaction_type', 'amount', 'payment_method',
        'gateway_transaction_id', 'gateway_response', 'balance_after',
        'created_at', 'completed_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': (
                'id', 'wallet', 'transaction_type', 'amount', 
                'balance_after', 'status'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method', 'gateway_transaction_id', 
                'gateway_response', 'description'
            )
        }),
        ('Verification', {
            'fields': ('verified_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.wallet.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'wallet__user__email'
    
    def amount_display(self, obj):
        color = 'green' if obj.transaction_type == 'credit' else 'red'
        symbol = '+' if obj.transaction_type == 'credit' else '-'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ৳{}</span>',
            color, symbol, obj.amount
        )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def balance_after_display(self, obj):
        return format_html(
            '<span style="color: #666;">৳{}</span>',
            obj.balance_after
        )
    balance_after_display.short_description = 'Balance After'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'completed': '#28A745',
            'failed': '#DC3545',
            'refunded': '#6C757D'
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_email', 'amount_display', 'total_questions',
        'status_badge', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'user__email', 'wallet_transaction__gateway_transaction_id'
    ]
    readonly_fields = [
        'id', 'user', 'wallet', 'amount', 'mcq_count', 'cq_count',
        'total_questions', 'mcq_price_per_question', 'cq_price_per_question',
        'draft', 'pdf_file', 'balance_after', 'wallet_transaction', 'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('User & Wallet', {
            'fields': ('id', 'user', 'wallet', 'wallet_transaction')
        }),
        ('Question Details', {
            'fields': (
                'mcq_count', 'cq_count', 'total_questions',
                'mcq_price_per_question', 'cq_price_per_question'
            )
        }),
        ('Payment Details', {
            'fields': ('amount', 'balance_after', 'status')
        }),
        ('Files', {
            'fields': ('draft', 'pdf_file')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def amount_display(self, obj):
        return format_html(
            '<span style="color: red; font-weight: bold;">৳{}</span>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'completed': '#28A745',
            'failed': '#DC3545',
            'refunded': '#6C757D'
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

