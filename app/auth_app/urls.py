from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('secure/', SecureDataView.as_view()),
    path('refresh/', RefreshTokenView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('logout-all/', LogoutAllDevicesView.as_view()),
]
