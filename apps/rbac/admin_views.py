"""
Admin Activity and Audit Log Views
Provides activity tracking for admin dashboard
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from datetime import timedelta

from apps.rbac.models import RoleHistory
from apps.payments.models import WalletTransaction


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def recent_activities(request):
    """
    Get recent system activities for admin dashboard
    
    Query params:
    - limit: Number of activities to return (default: 10)
    
    Requires: Admin user
    """
    
    limit = int(request.query_params.get('limit', 10))
    
    activities = []
    
    # Get recent role changes
    role_histories = RoleHistory.objects.select_related(
        'user', 'role', 'performed_by'
    ).order_by('-created_at')[:limit]
    
    for history in role_histories:
        actor_name = history.performed_by.get_full_name() if history.performed_by else 'System'
        actor_email = history.performed_by.email if history.performed_by else 'system@auto'
        
        action_text = {
            'assigned': f'Assigned {history.role.name} role to {history.user.get_full_name() or history.user.email}',
            'revoked': f'Revoked {history.role.name} role from {history.user.get_full_name() or history.user.email}',
            'expired': f'{history.role.name} role expired for {history.user.get_full_name() or history.user.email}',
            'modified': f'Modified {history.role.name} role for {history.user.get_full_name() or history.user.email}',
        }.get(history.action, f'{history.action} {history.role.name}')
        
        activities.append({
            'id': str(history.id),
            'actor': actor_name,
            'actor_email': actor_email,
            'action': action_text,
            'target_type': 'role',
            'target_id': str(history.role.id),
            'timestamp': history.created_at.isoformat(),
            'details': {
                'action_type': history.action,
                'role': history.role.name,
                'user': history.user.email,
                'reason': history.reason or ''
            }
        })
    
    # Get recent wallet transactions (top-ups)
    recent_transactions = WalletTransaction.objects.filter(
        transaction_type=WalletTransaction.CREDIT,
        status=WalletTransaction.COMPLETED
    ).select_related('wallet__user').order_by('-completed_at')[:limit//2]
    
    for txn in recent_transactions:
        activities.append({
            'id': f'txn_{txn.id}',
            'actor': txn.wallet.user.get_full_name() or txn.wallet.user.email,
            'actor_email': txn.wallet.user.email,
            'action': f'Wallet top-up of ৳{txn.amount} via {txn.get_payment_method_display()}',
            'target_type': 'wallet',
            'target_id': str(txn.wallet.id),
            'timestamp': txn.completed_at.isoformat() if txn.completed_at else txn.created_at.isoformat(),
            'details': {
                'action_type': 'wallet_topup',
                'amount': str(txn.amount),
                'payment_method': txn.payment_method,
                'transaction_id': str(txn.id)
            }
        })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response(activities[:limit])


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def activity_summary(request):
    """
    Get activity summary for the last 7 days
    
    Requires: Admin user
    """
    
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    
    # Role assignments this week
    role_assignments = RoleHistory.objects.filter(
        created_at__gte=week_ago,
        action='assigned'
    ).count()
    
    # Role revocations this week
    role_revocations = RoleHistory.objects.filter(
        created_at__gte=week_ago,
        action='revoked'
    ).count()
    
    # Completed transactions this week
    completed_transactions = WalletTransaction.objects.filter(
        completed_at__gte=week_ago,
        status=WalletTransaction.COMPLETED
    ).count()
    
    # Failed transactions this week
    failed_transactions = WalletTransaction.objects.filter(
        created_at__gte=week_ago,
        status=WalletTransaction.FAILED
    ).count()
    
    return Response({
        'period': '7_days',
        'role_assignments': role_assignments,
        'role_revocations': role_revocations,
        'completed_transactions': completed_transactions,
        'failed_transactions': failed_transactions,
        'total_activities': role_assignments + role_revocations + completed_transactions + failed_transactions
    })
