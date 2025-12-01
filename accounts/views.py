# accounts/views.py

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.encryption import TokenEncryption
from core.responses import (
    conflict_response,
    error_response,
    success_response,
    validation_error_response,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class LoginThrottle(AnonRateThrottle):
    rate = '5/minute'


class RefreshThrottle(AnonRateThrottle):
    rate = '10/minute'


class RegisterThrottle(AnonRateThrottle):
    rate = '3/hour'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        """Override to add custom claims"""
        token = super().get_token(user)
        
        token['username'] = user.username
        token['role'] = user.role
        token['is_admin'] = user.is_admin
        
        return token


class SecureLoginView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]
    
    def post(self, request, *args, **kwargs):
        """Handle login request with encryption and logging"""
        
        username = request.data.get('username', 'unknown')
        ip = self.get_client_ip(request)
        request_id = getattr(request, 'id', None)
        
        logger.info(
            f"Login attempt | username={username} | ip={ip} | request_id={request_id}"
        )
        
        if not username or not request.data.get('password'):
            logger.warning(
                f"Login failed - missing credentials | username={username} | ip={ip} | request_id={request_id}"
            )
            return validation_error_response(
                message="Username and password are required",
                errors={
                    "username": ["This field is required"] if not username else [],
                    "password": ["This field is required"] if not request.data.get('password') else []
                },
                request_id=request_id
            )
        
        try:
            response = super().post(request, *args, **kwargs)
            
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            
            encrypted_access = TokenEncryption.encrypt(access_token)
            encrypted_refresh = TokenEncryption.encrypt(refresh_token)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            
            logger.info(
                f"Login successful | user_id={user.id} | username={username} | role={user.role} | ip={ip} | request_id={request_id}"
            )
            
            return success_response(
                message="Login successful",
                data={
                    'access': encrypted_access,
                    'refresh': encrypted_refresh,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'is_admin': user.is_admin,
                    }
                },
                request_id=request_id
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(
                f"Login failed | username={username} | ip={ip} | error={error_msg} | request_id={request_id}"
            )
            
            if hasattr(e, 'detail'):
                return error_response(
                    message="Invalid credentials",
                    errors={"detail": error_msg},
                    status=status.HTTP_401_UNAUTHORIZED,
                    code="INVALID_CREDENTIALS",
                    request_id=request_id
                )
            
            return error_response(
                message="Login failed",
                errors={"detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
                code="LOGIN_FAILED",
                request_id=request_id
            )
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class SecureTokenRefreshView(TokenRefreshView):

    throttle_classes = [RefreshThrottle]
    
    def post(self, request, *args, **kwargs):
        """Handle token refresh with decryption and encryption"""
        
        request_id = getattr(request, 'id', None)
        
        logger.info(f"Token refresh attempt | request_id={request_id}")
        
        try:
            encrypted_refresh = request.data.get('refresh')
            
            if not encrypted_refresh:
                logger.warning(f"Token refresh failed - missing token | request_id={request_id}")
                return validation_error_response(
                    message="Refresh token is required",
                    errors={"refresh": ["This field is required"]},
                    request_id=request_id
                )
            
            try:
                decrypted_refresh = TokenEncryption.decrypt(encrypted_refresh)
            except ValueError as e:
                logger.warning(
                    f"Token refresh failed - decryption error | error={str(e)} | request_id={request_id}"
                )
                return error_response(
                    message="Invalid refresh token format",
                    errors={"refresh": ["Token decryption failed"]},
                    status=status.HTTP_401_UNAUTHORIZED,
                    code="INVALID_REFRESH_TOKEN",
                    request_id=request_id
                )
            
            request.data._mutable = True
            request.data['refresh'] = decrypted_refresh
            request.data._mutable = False
            
            response = super().post(request, *args, **kwargs)
            
            new_access = TokenEncryption.encrypt(response.data['access'])
            
            result = {'access': new_access}
            
            if 'refresh' in response.data:
                new_refresh = TokenEncryption.encrypt(response.data['refresh'])
                result['refresh'] = new_refresh
                logger.info(f"Token refreshed with rotation | request_id={request_id}")
            else:
                logger.info(f"Token refreshed | request_id={request_id}")
            
            return success_response(
                message="Token refreshed successfully",
                data=result,
                request_id=request_id
            )
            
        except ValueError as e:
            logger.warning(
                f"Token refresh failed - decryption error | error={str(e)} | request_id={request_id}"
            )
            return error_response(
                message="Invalid refresh token",
                status=status.HTTP_401_UNAUTHORIZED,
                code="INVALID_REFRESH_TOKEN",
                request_id=request_id
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.warning(
                f"Token refresh failed | error={error_msg} | request_id={request_id}"
            )
            
            if 'token' in error_msg.lower():
                return error_response(
                    message="Invalid or expired refresh token",
                    errors={"detail": error_msg},
                    status=status.HTTP_401_UNAUTHORIZED,
                    code="INVALID_REFRESH_TOKEN",
                    request_id=request_id
                )
            
            return error_response(
                message="Token refresh failed",
                errors={"detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
                code="REFRESH_FAILED",
                request_id=request_id
            )


class RegisterView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]
    
    def post(self, request, *args, **kwargs):
        """Handle user registration"""
        
        request_id = getattr(request, 'id', None)
        ip = self.get_client_ip(request)
        
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        
        logger.info(
            f"Registration attempt | username={username} | email={email} | ip={ip} | request_id={request_id}"
        )
        
        errors = {}
        
        if not username:
            errors['username'] = ['This field is required']
        elif len(username) < 3:
            errors['username'] = ['Username must be at least 3 characters']
        elif len(username) > 150:
            errors['username'] = ['Username must be less than 150 characters']
        
        if not email:
            errors['email'] = ['This field is required']
        elif '@' not in email or '.' not in email:
            errors['email'] = ['Enter a valid email address']
        
        if not password:
            errors['password'] = ['This field is required']
        elif len(password) < 8:
            errors['password'] = ['Password must be at least 8 characters']
        
        if errors:
            logger.warning(
                f"Registration failed - validation | username={username} | errors={list(errors.keys())} | ip={ip} | request_id={request_id}"
            )
            return validation_error_response(
                message="Validation failed",
                errors=errors,
                request_id=request_id
            )
        
        if User.objects.filter(username__iexact=username).exists():
            logger.warning(
                f"Registration failed - duplicate username | username={username} | ip={ip} | request_id={request_id}"
            )
            return conflict_response(
                message="Username already exists",
                errors={"username": ["This username is already taken"]},
                request_id=request_id
            )
        
        if User.objects.filter(email__iexact=email).exists():
            logger.warning(
                f"Registration failed - duplicate email | email={email} | ip={ip} | request_id={request_id}"
            )
            return conflict_response(
                message="Email already exists",
                errors={"email": ["This email is already registered"]},
                request_id=request_id
            )
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=User.Role.USER
                )
                
                logger.info(
                    f"Registration successful | user_id={user.id} | username={username} | email={email} | ip={ip} | request_id={request_id}"
                )
                
                serializer = CustomTokenObtainPairSerializer()
                token = serializer.get_token(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                
                encrypted_access = TokenEncryption.encrypt(access_token)
                encrypted_refresh = TokenEncryption.encrypt(refresh_token)
                
                return success_response(
                    message="Registration successful",
                    data={
                        'access': encrypted_access,
                        'refresh': encrypted_refresh,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'role': user.role,
                            'is_admin': user.is_admin,
                        }
                    },
                    status=status.HTTP_201_CREATED,
                    request_id=request_id
                )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Registration failed - unexpected error | username={username} | error={error_msg} | ip={ip} | request_id={request_id}",
                exc_info=True
            )
            
            if 'password' in error_msg.lower():
                return validation_error_response(
                    message="Password does not meet requirements",
                    errors={"password": [error_msg]},
                    request_id=request_id
                )
            
            return error_response(
                message="Registration failed",
                errors={"detail": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
                code="REGISTRATION_FAILED",
                request_id=request_id
            )
    
    @staticmethod
    def get_client_ip(request):
        """Extract real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class PasswordResetRequestThrottle(AnonRateThrottle):
    rate = '3/hour'


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    request_id = getattr(request, 'id', None)
    email = request.data.get('email', '').strip().lower()
    
    logger.info(f"Password reset requested | email={email} | request_id={request_id}")
    
    if not email:
        return validation_error_response(
            message="Email is required",
            errors={"email": ["This field is required"]},
            request_id=request_id
        )
    
    try:
        user = User.objects.get(email__iexact=email)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        subject = "Password Reset Request"
        message = f"""
Hello {user.username},

You requested to reset your password. Click the link below to reset it:

{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Your Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent | user_id={user.id} | email={email} | request_id={request_id}")
        
        return success_response(
            message="Password reset email sent. Please check your inbox.",
            request_id=request_id
        )
        
    except User.DoesNotExist:
        logger.warning(f"Password reset for non-existent email | email={email} | request_id={request_id}")
        
        return success_response(
            message="If that email exists, a reset link has been sent.",
            request_id=request_id
        )
    
    except Exception as e:
        logger.error(f"Password reset email failed | email={email} | error={str(e)} | request_id={request_id}")
        
        return error_response(
            message="Failed to send password reset email",
            errors={"detail": "Please try again later"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="EMAIL_SEND_FAILED",
            request_id=request_id
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    request_id = getattr(request, 'id', None)
    
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    logger.info(f"Password reset confirm attempt | uid={uid} | request_id={request_id}")
    
    errors = {}
    
    if not uid:
        errors['uid'] = ['This field is required']
    if not token:
        errors['token'] = ['This field is required']
    if not new_password:
        errors['password'] = ['This field is required']
    elif len(new_password) < 8:
        errors['password'] = ['Password must be at least 8 characters']
    
    if errors:
        return validation_error_response(
            message="Validation failed",
            errors=errors,
            request_id=request_id
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        
        if not default_token_generator.check_token(user, token):
            logger.warning(f"Invalid/expired token | user_id={user_id} | request_id={request_id}")
            return error_response(
                message="Invalid or expired reset link",
                errors={"token": ["This reset link is invalid or has expired"]},
                status=status.HTTP_400_BAD_REQUEST,
                code="INVALID_TOKEN",
                request_id=request_id
            )
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password reset successful | user_id={user.id} | username={user.username} | request_id={request_id}")
        
        return success_response(
            message="Password has been reset successfully. You can now login with your new password.",
            request_id=request_id
        )
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.warning(f"Invalid UID in password reset | uid={uid} | request_id={request_id}")
        return error_response(
            message="Invalid reset link",
            errors={"uid": ["Invalid user identification"]},
            status=status.HTTP_400_BAD_REQUEST,
            code="INVALID_UID",
            request_id=request_id
        )
    
    except Exception as e:
        logger.error(f"Password reset failed | error={str(e)} | request_id={request_id}")
        return error_response(
            message="Password reset failed",
            errors={"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
            code="RESET_FAILED",
            request_id=request_id
        )