"""
RBAC API Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Permission, Role, UserRole, RoleHistory
from .serializers import (
    PermissionSerializer, RoleSerializer, UserRoleSerializer,
    RoleHistorySerializer, UserPermissionsSerializer
)
from .serializers.user_serializer import UserWithRolesSerializer, UserCreateUpdateSerializer
from .permissions import HasPermission, MinimumRoleLevel

User = get_user_model()


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing permissions
    """
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'admin.roles'
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get permissions grouped by category"""
        categories = {}
        permissions = Permission.objects.filter(is_active=True)
        for permission in permissions:
            if permission.category not in categories:
                categories[permission.category] = []
            categories[permission.category].append(
                PermissionSerializer(permission).data
            )
        return Response(categories)


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles
    """
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'admin.roles'
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, slug=None):
        """Get all permissions for a role including inherited"""
        role = self.get_object()
        permissions = role.get_all_permissions()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def users(self, request, slug=None):
        """Get all users with this role"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(role=role, is_active=True)
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get role hierarchy"""
        roles = self.get_queryset().order_by('-level')
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user role assignments
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, MinimumRoleLevel]
    minimum_role_level = 60  # Manager level
    
    def get_queryset(self):
        """Filter by user if specified"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user', 'role', 'assigned_by')
    
    def perform_create(self, serializer):
        """Set assigned_by to current user"""
        serializer.save(assigned_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a role assignment"""
        user_role = self.get_object()
        user_role.is_active = False
        user_role.save()
        
        return Response({
            'message': f'Role {user_role.role.name} revoked from {user_role.user.email}'
        })
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set this role as primary for the user"""
        user_role = self.get_object()
        
        # Remove primary from other roles
        UserRole.objects.filter(
            user=user_role.user,
            is_primary=True
        ).update(is_primary=False)
        
        # Set this as primary
        user_role.is_primary = True
        user_role.save()
        
        return Response({
            'message': f'Role {user_role.role.name} set as primary for {user_role.user.email}'
        })


class RoleHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing role history
    """
    queryset = RoleHistory.objects.all()
    serializer_class = RoleHistorySerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'admin.logs'
    
    def get_queryset(self):
        """Filter by user if specified"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user', 'role', 'performed_by')


class CurrentUserRBACViewSet(viewsets.ViewSet):
    """
    ViewSet for current user's RBAC information
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='my-roles')
    def my_roles(self, request):
        """Get current user's roles"""
        user = request.user
        active_roles = user.get_active_roles()
        
        data = {
            'roles': [{'id': ur.role.id, 'name': ur.role.name, 'slug': ur.role.slug, 'level': ur.role.level, 'is_primary': ur.is_primary} for ur in active_roles],
            'primary_role': user.get_primary_role(),
            'role_level': user.get_role_level()
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='my-permissions')
    def my_permissions(self, request):
        """Get current user's permissions"""
        user = request.user
        permissions = user.get_all_permissions()
        
        data = {
            'permissions': PermissionSerializer(permissions, many=True).data,
            'permission_count': len(permissions)
        }
        
        return Response(data)
    
    @action(detail=False, methods=['post'], url_path='has-permission')
    def has_permission(self, request):
        """Check if current user has a specific permission"""
        permission_name = request.data.get('permission')
        
        if not permission_name:
            return Response(
                {'error': 'permission field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_perm = request.user.has_permission(permission_name)
        
        return Response({
            'permission': permission_name,
            'has_permission': has_perm
        })
    
    @action(detail=False, methods=['post'])
    def check_role(self, request):
        """Check if current user has a specific role"""
        role_name = request.data.get('role')
        
        if not role_name:
            return Response(
                {'error': 'role field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        has_role = request.user.has_role(role_name)
        
        return Response({
            'role': role_name,
            'has_role': has_role
        })


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (admin only)
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, MinimumRoleLevel]
    minimum_role_level = 60  # Manager level
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'email', 'first_name']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserWithRolesSerializer
    
    def get_queryset(self):
        """Get users with filtering"""
        queryset = super().get_queryset()
        
        # Filter by role
        role_type = self.request.query_params.get('role')
        if role_type:
            queryset = queryset.filter(
                user_roles__role__role_type=role_type,
                user_roles__is_active=True
            ).distinct()
        
        # Filter by status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.prefetch_related('user_roles__role__permissions')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': f'User {user.email} activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'message': f'User {user.email} deactivated'})
    
    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        try:
            user = self.get_object()
            email = user.email
            
            # Delete related records first
            UserRole.objects.filter(user=user).delete()
            RoleHistory.objects.filter(user=user).delete()
            
            user.delete()
            return Response(
                {'message': f'User {email} deleted successfully'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to delete user: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Count users by role
        from django.db.models import Count
        role_counts = UserRole.objects.filter(
            is_active=True,
            is_primary=True
        ).values('role__role_type').annotate(count=Count('id'))
        
        role_stats = {item['role__role_type']: item['count'] for item in role_counts}
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'role_distribution': role_stats
        })
