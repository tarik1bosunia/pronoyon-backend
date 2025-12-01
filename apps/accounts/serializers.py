"""
Custom serializers for authentication.
"""
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class UserRoleSerializer(serializers.Serializer):
    """Serializer for user role assignment"""
    id = serializers.IntegerField()
    role = serializers.SerializerMethodField()
    is_primary = serializers.BooleanField()
    is_active = serializers.BooleanField()
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    assigned_at = serializers.DateTimeField()
    
    def get_role(self, obj):
        """Return role details"""
        return {
            'id': obj.role.id,
            'name': obj.role.name,
            'slug': obj.role.slug,
            'level': obj.role.level,
            'role_type': obj.role.role_type,
            'description': obj.role.description,
        }


class PermissionSerializer(serializers.Serializer):
    """Serializer for permissions"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    codename = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()
    is_active = serializers.BooleanField()


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Custom user serializer that includes RBAC data (roles and permissions)
    """
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'roles',
            'permissions',
            'primary_role',
        )
        read_only_fields = ('email',)
    
    def get_roles(self, obj):
        """Get all active user roles"""
        user_roles = obj.get_active_roles()
        return UserRoleSerializer(user_roles, many=True).data
    
    def get_permissions(self, obj):
        """Get all user permissions from roles"""
        permissions = obj.get_all_permissions()
        return PermissionSerializer(permissions, many=True).data
    
    def get_primary_role(self, obj):
        """Get user's primary role"""
        primary_role = obj.get_primary_role()
        if primary_role:
            return {
                'id': primary_role.id,
                'name': primary_role.name,
                'slug': primary_role.slug,
                'level': primary_role.level,
                'role_type': primary_role.role_type,
                'description': primary_role.description,
            }
        return None


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer that removes username field
    since we use email as the unique identifier.
    """
    username = None  # Remove username field
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    
    def validate_email(self, email):
        """
        Validate that email is unique.
        """
        email = email.lower().strip()
        
        # Check if user with this email already exists
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        
        return email
    
    def get_cleaned_data(self):
        """
        Return cleaned data without username field.
        """
        return {
            'email': self.validated_data.get('email', ''), # type: ignore
            'password1': self.validated_data.get('password1', ''), # type: ignore
            'first_name': self.validated_data.get('first_name', ''), # type: ignore
            'last_name': self.validated_data.get('last_name', ''), # type: ignore
        }
    
    def save(self, request):
        """
        Override save to handle integrity errors gracefully.
        """
        try:
            return super().save(request)
        except IntegrityError as e:
            error_msg = str(e)
            if 'email' in error_msg.lower():
                raise serializers.ValidationError({
                    'email': ['A user with this email already exists.']
                })
            raise serializers.ValidationError(
                'An error occurred while creating the user. Please try again.'
            )



# apps/authentication/serializers.py
from rest_framework import serializers

class GoogleLoginSerializer(serializers.Serializer):
    auth_token = serializers.CharField(required=True)