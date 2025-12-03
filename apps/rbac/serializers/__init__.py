"""
RBAC Serializers
"""
from rest_framework import serializers
from ..models import Permission, Role, UserRole, RoleHistory


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description', 'category', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class PermissionListSerializer(serializers.ModelSerializer):
    """Minimal permission serializer for lists"""
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'category']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionListSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True,
        queryset=Permission.objects.all(),
        source='permissions'
    )
    user_count = serializers.IntegerField(read_only=True, source='get_user_count')
    all_permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'slug', 'description', 'role_type', 'level',
            'permissions', 'permission_ids', 'all_permissions',
            'inherits_from', 'is_active', 'is_default', 'max_users',
            'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_all_permissions(self, obj):
        """Get all permissions including inherited"""
        permissions = obj.get_all_permissions()
        return PermissionListSerializer(permissions, many=True).data


class RoleListSerializer(serializers.ModelSerializer):
    """Minimal role serializer for lists"""
    user_count = serializers.IntegerField(read_only=True, source='get_user_count')
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'level', 'user_count', 'is_active']


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleListSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Role.objects.filter(is_active=True),
        source='role'
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    assigned_by_email = serializers.EmailField(source='assigned_by.email', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_email', 'role', 'role_id',
            'is_active', 'is_primary', 'assigned_by', 'assigned_by_email',
            'assigned_at', 'expires_at', 'is_expired', 'context', 'notes'
        ]
        read_only_fields = ['id', 'assigned_at']


class RoleHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)
    
    class Meta:
        model = RoleHistory
        fields = [
            'id', 'user', 'user_email', 'role', 'role_name',
            'action', 'performed_by', 'performed_by_email',
            'reason', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer for user's permissions"""
    permissions = PermissionListSerializer(many=True, read_only=True)
    roles = RoleListSerializer(many=True, read_only=True)
    primary_role = RoleListSerializer(read_only=True)
    role_level = serializers.IntegerField(read_only=True)
