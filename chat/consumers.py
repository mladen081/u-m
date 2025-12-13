# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import json
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    
    connected_users = {}
    
    async def connect(self):
        self.room_group_name = 'global_chat'
        
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        ChatConsumer.connected_users[self.channel_name] = {
            'user_id': self.scope['user'].id,
            'username': self.scope['user'].username,
        }
        
        await self.accept()
        logger.info(f"User {self.scope['user'].username} connected to chat")
        
        await self.broadcast_user_list()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            if self.channel_name in ChatConsumer.connected_users:
                del ChatConsumer.connected_users[self.channel_name]
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User disconnected from chat: {close_code}")
            
            await self.broadcast_user_list()
    
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
            'action': 'new_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))
    
    async def clear_all_messages(self, event):
        await self.send(text_data=json.dumps({
            'action': 'clear_all',
        }))
    
    async def user_list_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'user_list_update',
            'users': event['users'],
        }))
    
    async def broadcast_user_list(self):
        unique_users = {}
        for channel_data in ChatConsumer.connected_users.values():
            user_id = channel_data['user_id']
            if user_id not in unique_users:
                unique_users[user_id] = channel_data['username']
        
        user_list = list(unique_users.values())
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list_update',
                'users': user_list,
            }
        )
    
    @database_sync_to_async
    def save_message(self, user, content):
        from .models import Message
        return Message.objects.create(user=user, content=content)