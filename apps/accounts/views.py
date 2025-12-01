# apps/authentication/views.py
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import GoogleLoginSerializer
from .google import Google

User = get_user_model()

class GoogleLoginView(GenericAPIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        auth_token = serializer.validated_data.get('auth_token')
        
        # 1. Validate with Google
        user_data = Google.validate(auth_token)
        
        # 2. Extract data
        # Google returns 'sub' as the unique ID, but we mainly use email
        email = user_data.get('email')
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')
        email_verified = user_data.get('email_verified', False)
        
        if not email:
            return Response({'detail': 'Email not provided by Google.'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Get or Create User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            }
        )

        if not user.is_active:
            raise AuthenticationFailed('This account has been deactivated.')

        update_fields: list[str] = []

        if created:
            user.set_unusable_password()
            update_fields.append('password')
            user.is_verified = email_verified or user.is_verified
            update_fields.append('is_verified')

        # Only update empty profile fields so we don't overwrite user-provided data
        if first_name and not user.first_name:
            user.first_name = first_name
            update_fields.append('first_name')
        if last_name and not user.last_name:
            user.last_name = last_name
            update_fields.append('last_name')

        if email_verified and not user.is_verified:
            user.is_verified = True
            update_fields.append('is_verified')

        metadata = user.metadata or {}
        if metadata.get('auth_provider') != 'google':
            metadata['auth_provider'] = 'google'
            metadata['google_sub'] = user_data.get('sub')
            user.metadata = metadata
            update_fields.append('metadata')

        if update_fields:
            user.save(update_fields=list(set(update_fields)))
        
        # 4. Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        
        # Serialize user with RBAC data
        from .serializers import UserDetailsSerializer
        user_data = UserDetailsSerializer(user).data
        
        return Response({
            'user': user_data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)