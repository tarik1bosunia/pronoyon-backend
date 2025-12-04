"""
Admin Payment Statistics Views
Provides aggregated payment data for admin dashboard
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import WalletBalance, WalletTransaction, PaymentTransaction


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def payment_statistics(request):
    """
    Get comprehensive payment statistics for admin dashboard
    
    Requires: Admin user
    """
    
    # Calculate date ranges
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    
    # Get all transactions
    all_transactions = WalletTransaction.objects.all()
    
    # Transaction counts by status
    transaction_stats = all_transactions.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=WalletTransaction.COMPLETED)),
        pending=Count('id', filter=Q(status=WalletTransaction.PENDING)),
        failed=Count('id', filter=Q(status=WalletTransaction.FAILED)),
        refunded=Count('id', filter=Q(status=WalletTransaction.REFUNDED))
    )
    
    # Revenue calculations (completed credit transactions)
    completed_credits = all_transactions.filter(
        transaction_type=WalletTransaction.CREDIT,
        status=WalletTransaction.COMPLETED
    )
    
    total_revenue = completed_credits.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # This week's revenue
    this_week_revenue = completed_credits.filter(
        completed_at__gte=week_ago
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Last week's revenue for percentage calculation
    last_week_revenue = completed_credits.filter(
        completed_at__gte=two_weeks_ago,
        completed_at__lt=week_ago
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Calculate percentage change
    if last_week_revenue > 0:
        revenue_percentage_change = float(
            ((this_week_revenue - last_week_revenue) / last_week_revenue) * 100
        )
    else:
        revenue_percentage_change = 100.0 if this_week_revenue > 0 else 0.0
    
    # Average transaction amount
    avg_transaction = completed_credits.aggregate(
        avg=Avg('amount')
    )['avg'] or Decimal('0.00')
    
    # Transaction type breakdown
    transaction_types = all_transactions.filter(
        status=WalletTransaction.COMPLETED
    ).aggregate(
        top_up=Count('id', filter=Q(transaction_type=WalletTransaction.CREDIT)),
        debit=Count('id', filter=Q(transaction_type=WalletTransaction.DEBIT))
    )
    
    return Response({
        'total_transactions': transaction_stats['total'],
        'total_revenue': str(total_revenue),
        'pending_transactions': transaction_stats['pending'],
        'completed_transactions': transaction_stats['completed'],
        'failed_transactions': transaction_stats['failed'],
        'refunded_transactions': transaction_stats['refunded'],
        'revenue_this_week': str(this_week_revenue),
        'revenue_percentage_change': round(revenue_percentage_change, 2),
        'average_transaction': str(avg_transaction),
        'top_up_count': transaction_types['top_up'],
        'debit_count': transaction_types['debit']
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def recent_transactions(request):
    """
    Get recent wallet transactions for admin dashboard
    
    Query params:
    - limit: Number of transactions to return (default: 10)
    
    Requires: Admin user
    """
    
    limit = int(request.query_params.get('limit', 10))
    
    transactions = WalletTransaction.objects.select_related(
        'wallet__user'
    ).order_by('-created_at')[:limit]
    
    data = []
    for txn in transactions:
        data.append({
            'id': str(txn.id),
            'user_email': txn.wallet.user.email,
            'user_name': txn.wallet.user.get_full_name() or txn.wallet.user.email,
            'amount': str(txn.amount),
            'transaction_type': txn.transaction_type,
            'payment_method': txn.get_payment_method_display(),
            'status': txn.get_status_display(),
            'created_at': txn.created_at.isoformat()
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def wallet_overview(request):
    """
    Get wallet overview statistics
    
    Requires: Admin user
    """
    
    wallets = WalletBalance.objects.all()
    
    stats = wallets.aggregate(
        total_wallets=Count('id'),
        active_wallets=Count('id', filter=Q(is_active=True)),
        total_balance=Sum('balance'),
        total_credited=Sum('total_credited'),
        total_debited=Sum('total_debited')
    )
    
    return Response({
        'total_wallets': stats['total_wallets'],
        'active_wallets': stats['active_wallets'],
        'total_balance': str(stats['total_balance'] or Decimal('0.00')),
        'total_credited': str(stats['total_credited'] or Decimal('0.00')),
        'total_debited': str(stats['total_debited'] or Decimal('0.00'))
    })
