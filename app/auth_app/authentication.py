from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .utils import decode_jwt

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        payload = decode_jwt(token)
        if not payload:
            raise AuthenticationFailed('Invalid or expired token')
        try:
            user = User.objects.get(id=payload['id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        return (user, None)
