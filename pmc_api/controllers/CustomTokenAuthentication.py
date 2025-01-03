from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from oauth2_provider.models import AccessToken
from django.utils.timezone import now


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom authentication class to validate tokens from the AccessToken table.
    """

    def authenticate(self, request):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None  # No token provided, fallback to other authentication

        # Ensure the token is in the correct format: "Bearer <token>"
        try:
            token_type, access_token = auth_header.split()
            if token_type.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token type.')
        except ValueError:
            raise AuthenticationFailed('Invalid authorization header format.')

        # Validate the token against the AccessToken table
        try:
            token = AccessToken.objects.get(token=access_token)
            if token.expires < now():
                raise AuthenticationFailed('Token has expired.')
            # if not token.user.is_active:
            #     raise AuthenticationFailed('User is inactive.')
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed('Invalid or non-existent token.')

        # Return the associated user and token
        return (token.user, token)

    def authenticate_header(self, request):
        return 'Bearer'
