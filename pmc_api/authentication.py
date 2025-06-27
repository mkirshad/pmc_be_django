from rest_framework_simplejwt.authentication import JWTAuthentication
from pmc_api.threadlocals import set_current_user

class JWTAuthenticationWithUserTracking(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, _ = result
            set_current_user(user)  # 🔐 Set user into thread-local
        return result
