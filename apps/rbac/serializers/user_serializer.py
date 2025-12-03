"""
User serializers for admin user management
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.rbac.models import UserRole, Role
from apps.rbac.serializers import RoleSerializer

User = get_user_model()


class UserWithRolesSerializer(serializers.ModelSerializer):
    """Serializer for User with RBAC information"""
    roles = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'date_joined', 'last_login',
            'roles', 'primary_role'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email.split('@')[0]
    
    def get_roles(self, obj):
        """Get all active roles for the user"""
        user_roles = UserRole.objects.filter(
            user=obj,
            is_active=True
        ).select_related('role').prefetch_related('role__permissions')
        
        return [{
            'id': ur.pk,
            'role': RoleSerializer(ur.role).data,
            'is_primary': ur.is_primary,
            'is_active': ur.is_active,
            'assigned_at': ur.assigned_at,
            'expires_at': ur.expires_at,
        } for ur in user_roles]
    
    def get_primary_role(self, obj):
        """Get user's primary role"""
        try:
            primary_user_role = UserRole.objects.get(
                user=obj,
                is_primary=True,
                is_active=True
            )
            return RoleSerializer(primary_user_role.role).data
        except UserRole.DoesNotExist:
            return None


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating users"""
    role_id = serializers.IntegerField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'is_active', 'password', 'role_id'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Create a new user with optional role"""
        role_id = validated_data.pop('role_id', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create_user(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        # Assign role if provided
        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                UserRole.objects.create(
                    user=user,
                    role=role,
                    is_primary=True,
                    is_active=True
                )
            except Role.DoesNotExist:
                pass
        
        return user
    
    def update(self, instance, validated_data):
        """Update user information"""
        role_id = validated_data.pop('role_id', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Update role if provided
        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                # Deactivate existing primary role
                UserRole.objects.filter(
                    user=instance,
                    is_primary=True
                ).update(is_primary=False)
                
                # Set new primary role
                user_role, created = UserRole.objects.get_or_create(
                    user=instance,
                    role=role,
                    defaults={'is_primary': True, 'is_active': True}
                )
                if not created:
                    user_role.is_primary = True
                    user_role.is_active = True
                    user_role.save()
            except Role.DoesNotExist:
                pass
        
        return instance
