# chat/middleware.py
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from core.encryption import TokenEncryption
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_string):
    try:
        try:
            decrypted_token = TokenEncryption.decrypt(token_string)
            token = AccessToken(decrypted_token)
        except:
            token = AccessToken(token_string)
        
        user_id = token['user_id']
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {str(e)}")
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