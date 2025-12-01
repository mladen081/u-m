# accounts/urls.py

from django.urls import path

from .views import (
    RegisterView,
    SecureLoginView,
    SecureTokenRefreshView,
    password_reset_confirm,
    password_reset_request,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', SecureLoginView.as_view(), name='login'),
    path('token/refresh/', SecureTokenRefreshView.as_view(), name='token_refresh'),

    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
]