"""
Security and Authentication Management Views
Provides security monitoring and session management for admin
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def security_overview(request):
    """
    Get security overview statistics
    
    Requires: Admin user
    """
    
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Active sessions (outstanding tokens not blacklisted)
    outstanding_tokens = OutstandingToken.objects.filter(
        expires_at__gt=now
    ).exclude(
        id__in=BlacklistedToken.objects.values_list('token_id', flat=True)
    ).count()
    
    # Login attempts today (users with recent last_login)
    login_attempts_today = User.objects.filter(
        last_login__date=today
    ).count()
    
    # Failed login attempts (you may want to implement a failed login tracking model)
    # For now, using blacklisted tokens as proxy
    failed_attempts_today = BlacklistedToken.objects.filter(
        blacklisted_at__date=today
    ).count()
    
    # Active users this week
    active_users_week = User.objects.filter(
        last_login__gte=week_ago,
        is_active=True
    ).count()
    
    # Suspicious activities (multiple failed attempts, etc.)
    # This is a placeholder - implement actual suspicious activity tracking
    suspicious_activities = 0
    
    # Users by authentication method
    google_users = User.objects.filter(google_id__isnull=False).count()
    email_users = User.objects.filter(google_id__isnull=True).count()
    
    # Two-factor authentication (if implemented)
    two_factor_enabled = 0  # Placeholder for 2FA feature
    
    return Response({
        'active_sessions': outstanding_tokens,
        'login_attempts_today': login_attempts_today,
        'failed_attempts_today': failed_attempts_today,
        'active_users_week': active_users_week,
        'suspicious_activities': suspicious_activities,
        'authentication_methods': {
            'google': google_users,
            'email': email_users
        },
        'two_factor_enabled': two_factor_enabled,
        'last_updated': now.isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def active_sessions(request):
    """
    Get list of active user sessions
    
    Query params:
    - limit: Number of sessions to return (default: 20)
    - offset: Pagination offset (default: 0)
    
    Requires: Admin user
    """
    
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    
    now = timezone.now()
    
    # Get active tokens
    active_tokens = OutstandingToken.objects.filter(
        expires_at__gt=now
    ).exclude(
        id__in=BlacklistedToken.objects.values_list('token_id', flat=True)
    ).select_related('user').order_by('-created_at')[offset:offset+limit]
    
    sessions = []
    for token in active_tokens:
        if token.user:
            sessions.append({
                'id': str(token.id),
                'user': {
                    'id': str(token.user.id),
                    'email': token.user.email,
                    'full_name': token.user.get_full_name() or 'N/A',
                },
                'created_at': token.created_at.isoformat(),
                'expires_at': token.expires_at.isoformat(),
                'last_activity': token.user.last_login.isoformat() if token.user.last_login else None,
                'ip_address': 'N/A',  # Implement IP tracking if needed
                'user_agent': 'N/A',  # Implement user agent tracking if needed
            })
    
    total_count = OutstandingToken.objects.filter(
        expires_at__gt=now
    ).exclude(
        id__in=BlacklistedToken.objects.values_list('token_id', flat=True)
    ).count()
    
    return Response({
        'sessions': sessions,
        'total': total_count,
        'limit': limit,
        'offset': offset
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def revoke_session(request):
    """
    Revoke a specific user session
    
    Body:
    - token_id: ID of the token to revoke
    
    Requires: Admin user
    """
    
    token_id = request.data.get('token_id')
    
    if not token_id:
        return Response({'error': 'token_id is required'}, status=400)
    
    try:
        token = OutstandingToken.objects.get(id=token_id)
        BlacklistedToken.objects.get_or_create(token=token)
        
        return Response({
            'message': 'Session revoked successfully',
            'token_id': token_id
        })
    except OutstandingToken.DoesNotExist:
        return Response({'error': 'Token not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def revoke_user_sessions(request):
    """
    Revoke all sessions for a specific user
    
    Body:
    - user_id: ID of the user whose sessions to revoke
    
    Requires: Admin user
    """
    
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({'error': 'user_id is required'}, status=400)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Blacklist all active tokens for this user
        active_tokens = OutstandingToken.objects.filter(
            user=user,
            expires_at__gt=timezone.now()
        ).exclude(
            id__in=BlacklistedToken.objects.values_list('token_id', flat=True)
        )
        
        revoked_count = 0
        for token in active_tokens:
            BlacklistedToken.objects.get_or_create(token=token)
            revoked_count += 1
        
        return Response({
            'message': f'Revoked {revoked_count} session(s) for user {user.email}',
            'user_id': user_id,
            'revoked_count': revoked_count
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def login_history(request):
    """
    Get login history for all users
    
    Query params:
    - limit: Number of records to return (default: 50)
    - user_id: Filter by specific user
    
    Requires: Admin user
    """
    
    limit = int(request.query_params.get('limit', 50))
    user_id = request.query_params.get('user_id')
    
    queryset = User.objects.filter(last_login__isnull=False)
    
    if user_id:
        queryset = queryset.filter(id=user_id)
    
    users = queryset.order_by('-last_login')[:limit]
    
    history = []
    for user in users:
        history.append({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name() or 'N/A',
            },
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'date_joined': user.date_joined.isoformat(),
            'is_active': user.is_active,
            'authentication_method': 'google' if user.google_id else 'email',
        })
    
    return Response({
        'history': history,
        'total': queryset.count(),
        'limit': limit
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def security_logs(request):
    """
    Get security event logs
    
    Query params:
    - limit: Number of logs to return (default: 50)
    - event_type: Filter by event type (login, logout, failed_login, session_revoked)
    
    Requires: Admin user
    """
    
    limit = int(request.query_params.get('limit', 50))
    event_type = request.query_params.get('event_type')
    
    logs = []
    
    # Get blacklisted tokens (logout/revoked sessions)
    blacklisted = BlacklistedToken.objects.select_related(
        'token__user'
    ).order_by('-blacklisted_at')[:limit]
    
    for bl in blacklisted:
        if bl.token and bl.token.user:
            logs.append({
                'id': str(bl.id),
                'event_type': 'session_revoked',
                'user': {
                    'id': str(bl.token.user.id),
                    'email': bl.token.user.email,
                    'full_name': bl.token.user.get_full_name() or 'N/A',
                },
                'timestamp': bl.blacklisted_at.isoformat(),
                'details': {
                    'reason': 'Token blacklisted',
                    'token_id': str(bl.token.id)
                }
            })
    
    # Sort by timestamp
    logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Filter by event type if specified
    if event_type:
        logs = [log for log in logs if log['event_type'] == event_type]
    
    return Response({
        'logs': logs[:limit],
        'total': len(logs)
    })
