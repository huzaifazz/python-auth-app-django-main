from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_jwt, decode_jwt, generate_tokens, generate_email_token, verify_email_token
from rest_framework.permissions import IsAuthenticated
from .authentication import JWTAuthentication
from django.contrib.auth.models import User
from .signals import refresh_token_used, user_logged_in, secure_data_token_used, logging
from .models import BlacklistedToken, RefreshSession, OTP
from .serializers import RegisterSerializer
from django.urls import reverse
from django.core.mail import send_mail
import random

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
            try:
                BlacklistedToken.objects.get_or_create(token=session.token, user=user)  # refresh
            except Exception:
                pass
            if session.access_token:
                try:
                    BlacklistedToken.objects.get_or_create(token=session.access_token, user=user)  # access
                except Exception:
                    pass

        sessions.delete()  # Optional: Clean up

        return Response({'message': 'All sessions for this user have been revoked.'}, status=200)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate token and send email
            token = generate_email_token(user)
            verify_url = request.build_absolute_uri(
                reverse('verify-email') + f'?token={token}'
            )
            

            send_mail(
                'Verify Your Email',
                f'Click the link to verify your account: {verify_url}',
                'noreply@authapp.com',
                [user.email],
                fail_silently=False
            )

            return Response({'message': 'Registration successful. Please check your email to activate your account.'}, status=201)
        return Response(serializer.errors, status=400)
    
    
class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        email = verify_email_token(token)

        if not email:
            return Response({'error': 'Invalid or expired token'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=404)

        user.is_active = True
        user.save()

        return Response({'message': 'Email verified. You can now login.'})


class RequestOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)

        user, created = User.objects.get_or_create(email=email, username=email)
        otp_code = f"{random.randint(100000, 999999)}"

        # Save OTP
        OTP.objects.create(user=user, code=otp_code)

        # Send OTP via email
        send_mail(
            subject="Your Login OTP",
            message=f"Your OTP is: {otp_code}",
            from_email='noreply@authapp.com',
            recipient_list=[email],
            fail_silently=False
        )

        return Response({'message': 'OTP sent successfully.'}, status=200)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=404)

        latest_otp = OTP.objects.filter(user=user, code=otp, is_used=False).order_by('-created_at').first()
        if not latest_otp:
            return Response({'error': 'Invalid OTP'}, status=400)

        if latest_otp.is_expired():
            return Response({'error': 'OTP expired'}, status=400)

        latest_otp.is_used = True
        latest_otp.save()

        tokens = generate_tokens(user)
        return Response({'message': 'Login successful', 'tokens': tokens}, status=200)

