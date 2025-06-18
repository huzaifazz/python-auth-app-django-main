from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_jwt, decode_jwt, generate_tokens
from rest_framework.permissions import IsAuthenticated
from .authentication import JWTAuthentication
from django.contrib.auth.models import User
from .signals import refresh_token_used, user_logged_in, secure_data_token_used, logging
from .models import BlacklistedToken, RefreshSession

logger = logging.getLogger('auth_app')

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            user_logged_in.send(sender=LoginView, user=user, request=request)
            token = generate_tokens(user)
            return Response({'token': token}, status=status.HTTP_200_OK)
        ip = request.META.get('REMOTE_ADDR')
        logger.warning(f"Failed login for username: '{username}' from IP: {ip}")
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SecureDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        secure_data_token_used.send(sender=SecureDataView, request=request)
        return Response({
            'message': f'Hello, {request.user.username}. You’ve accessed a protected endpoint.'
        }, status=status.HTTP_200_OK)

        
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        # Check blacklist
        if BlacklistedToken.objects.filter(token=refresh_token).exists():
            return Response({'error': 'Token has been revoked'}, status=status.HTTP_403_FORBIDDEN)

        payload = decode_jwt(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Blacklist the old token (rotation logic)
        BlacklistedToken.objects.create(token=refresh_token)

        # Generate new access and refresh tokens
        tokens = generate_tokens(user)

        # Emit signal for logging or audit
        refresh_token_used.send(sender=RefreshTokenView, user=user, request=request)
        return Response(tokens, status=status.HTTP_200_OK)
    
    
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            BlacklistedToken.objects.get_or_create(token=refresh_token)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
    
class LogoutAllDevicesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        sessions = RefreshSession.objects.filter(user=user)

        for session in sessions:
            BlacklistedToken.objects.get_or_create(token=session.token, user=user)

        # Optional: clean up session list
        sessions.delete()

        return Response({'message': 'All sessions have been logged out.'}, status=200)

