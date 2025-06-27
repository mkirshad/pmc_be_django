import threading

_user = threading.local()

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Save user only if authenticated
        _user.value = getattr(request, "user", None) if request.user.is_authenticated else None
        response = self.get_response(request)
        return response

def get_current_user():
    return getattr(_user, 'value', None)
