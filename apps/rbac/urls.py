"""
RBAC URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PermissionViewSet, RoleViewSet, UserRoleViewSet,
    RoleHistoryViewSet, CurrentUserRBACViewSet, UserViewSet
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
]
