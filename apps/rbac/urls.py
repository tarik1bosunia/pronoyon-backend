"""
RBAC URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PermissionViewSet, RoleViewSet, UserRoleViewSet,
    RoleHistoryViewSet, CurrentUserRBACViewSet, UserViewSet
)
from .admin_views import recent_activities, activity_summary
from .security_views import (
    security_overview, active_sessions, revoke_session,
    revoke_user_sessions, login_history, security_logs
)

app_name = 'rbac'

router = DefaultRouter()
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'user-roles', UserRoleViewSet, basename='userrole')
router.register(r'history', RoleHistoryViewSet, basename='role-history')
router.register(r'me', CurrentUserRBACViewSet, basename='current-user-rbac')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # Admin activity endpoints
    path('activities/recent/', recent_activities, name='recent-activities'),
    path('activities/summary/', activity_summary, name='activity-summary'),
    # Security endpoints
    path('security/overview/', security_overview, name='security-overview'),
    path('security/sessions/', active_sessions, name='active-sessions'),
    path('security/sessions/revoke/', revoke_session, name='revoke-session'),
    path('security/sessions/revoke-user/', revoke_user_sessions, name='revoke-user-sessions'),
    path('security/login-history/', login_history, name='login-history'),
    path('security/logs/', security_logs, name='security-logs'),
]
