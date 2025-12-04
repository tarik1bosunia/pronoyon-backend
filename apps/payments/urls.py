"""
Payment app URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, PaymentViewSet, payment_callback
from .admin_views import payment_statistics, recent_transactions, wallet_overview

app_name = 'payments'

router = DefaultRouter()
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'transactions', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('callback/', payment_callback, name='payment-callback'),
    # Admin statistics endpoints
    path('stats/', payment_statistics, name='payment-stats'),
    path('transactions/recent/', recent_transactions, name='recent-transactions'),
    path('wallets/overview/', wallet_overview, name='wallet-overview'),
]
