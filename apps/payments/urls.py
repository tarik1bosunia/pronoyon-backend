"""
Payment app URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, PaymentViewSet, payment_callback

app_name = 'payments'

router = DefaultRouter()
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'transactions', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('callback/', payment_callback, name='payment-callback'),
]
