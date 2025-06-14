from django.urls import path
from .views import LoginView, SecureDataView, RefreshTokenView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('secure/', SecureDataView.as_view()),
    path('refresh/', RefreshTokenView.as_view()),
]
