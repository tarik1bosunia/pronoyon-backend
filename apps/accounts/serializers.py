"""
Custom serializers for authentication.
"""
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer that removes username field
    since we use email as the unique identifier.
    """
    username = None  # Remove username field
    
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
