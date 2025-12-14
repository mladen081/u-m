# chat/middleware.py

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
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
        query_string = scope.get('query_string', b'').decode()
        token = None
        
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if token:
            from urllib.parse import unquote
            token = unquote(token)
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)