from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_jwt, decode_jwt, generate_tokens
from rest_framework.permissions import IsAuthenticated
from .authentication import JWTAuthentication
from django.contrib.auth.models import User


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token = generate_tokens(user)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SecureDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': f'Hello, {request.user.username}. You’ve accessed a protected endpoint.'
        }, status=status.HTTP_200_OK)
        
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        payload = decode_jwt(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return Response({'error': 'Invalid refresh token'}, status=401)
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({'error': 'User not found'}, status=404)
        tokens = generate_tokens(user)
        return Response(tokens)
