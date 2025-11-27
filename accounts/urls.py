# accounts/urls.py

from django.urls import path
from .views import SecureLoginView, SecureTokenRefreshView, RegisterView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', SecureLoginView.as_view(), name='login'),
    path('token/refresh/', SecureTokenRefreshView.as_view(), name='token_refresh'),
]