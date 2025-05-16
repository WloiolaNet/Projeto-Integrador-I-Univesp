# saima/middleware.py

from django.contrib.auth import get_user_model
from threading import local

_user = local()

def get_current_user():
    return getattr(_user, 'user', None)

# No middleware, você define o usuário no contexto atual da requisição
class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            _user.user = request.user
        else:
            _user.user = None

        response = self.get_response(request)
        return response
