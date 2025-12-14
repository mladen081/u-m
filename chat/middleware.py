# chat/middleware.py

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_string):
    try:
        token = AccessToken(token_string)
        user_id = token.get('user_id')
        
        if not user_id:
            raise InvalidToken('No user_id in token')
        
        user = User.objects.get(id=user_id)
        
        if not user.is_active:
            raise InvalidToken('User is inactive')
            
        return user
        
    except (InvalidToken, TokenError) as e:
        logger.warning(f"Invalid token: {str(e)}")
        return AnonymousUser()
    except User.DoesNotExist:
        logger.warning(f"User not found for token")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket auth: {str(e)}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        cookies = {}
        
        if b'cookie' in headers:
            cookie_header = headers[b'cookie'].decode()
            for cookie in cookie_header.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key] = value
        
        token = cookies.get('access_token')
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)