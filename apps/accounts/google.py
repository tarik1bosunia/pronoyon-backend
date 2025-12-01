import requests
from rest_framework.exceptions import AuthenticationFailed


class Google:
    """Utility class to validate Google OAuth2 access tokens."""

    USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

    @staticmethod
    def validate(access_token: str) -> dict:
        """Validate a Google OAuth access token and return the associated profile."""
        try:
            response = requests.get(
                Google.USERINFO_URL,
                params={'access_token': access_token},
                timeout=5,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure path
            raise AuthenticationFailed('Unable to verify Google credentials.') from exc

        if not response.ok:
            raise AuthenticationFailed('The token is invalid or expired.')

        user_info = response.json()

        if not user_info.get('email'):
            raise AuthenticationFailed('Google account did not return an email address.')

        if user_info.get('email_verified') is False:
            raise AuthenticationFailed('Google account email is not verified.')

        return user_info