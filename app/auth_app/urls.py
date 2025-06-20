from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('secure/', SecureDataView.as_view()),
    path('refresh/', RefreshTokenView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('logout-all/', LogoutAllDevicesView.as_view()),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
]
