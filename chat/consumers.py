# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import json
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'global_chat'
        
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.scope['user'].username} connected to chat")
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User disconnected from chat: {close_code}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            
            if not message or len(message) > 1000:
                return
            
            user = self.scope['user']
            saved_message = await self.save_message(user, message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username,
                    'user_id': user.id,
                    'timestamp': saved_message.timestamp.isoformat(),
                    'message_id': saved_message.id,
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))
    
    @database_sync_to_async
    def save_message(self, user, content):
        from .models import Message
        return Message.objects.create(user=user, content=content)