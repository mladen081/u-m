# chat/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUser
from core.responses import success_response, error_response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message
from .consumers import ChatConsumer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    request_id = getattr(request, 'id', None)
    
    try:
        limit = int(request.GET.get('limit', 50))
        limit = min(limit, 100)
        
        messages = Message.objects.select_related('user').all()[:limit]
        
        data = [
            {
                'id': msg.id,
                'message': msg.content,
                'username': msg.user.username,
                'user_id': msg.user.id,
                'timestamp': msg.timestamp.isoformat(),
            }
            for msg in reversed(messages)
        ]
        
        logger.info(f"Messages retrieved | count={len(data)} | user={request.user.username} | request_id={request_id}")
        
        return success_response(
            message="Messages retrieved successfully",
            data=data,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Error retrieving messages | error={str(e)} | request_id={request_id}")
        return error_response(
            message="Failed to retrieve messages",
            errors={"detail": str(e)},
            request_id=request_id
        )


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_all_messages(request):
    request_id = getattr(request, 'id', None)
    
    try:
        count = Message.objects.count()
        Message.objects.all().delete()
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'global_chat',
            {
                'type': 'clear_all_messages',
            }
        )
        
        logger.info(f"All messages deleted | count={count} | admin={request.user.username} | request_id={request_id}")
        
        return success_response(
            message=f"All messages deleted successfully ({count} messages)",
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Error deleting messages | error={str(e)} | request_id={request_id}")
        return error_response(
            message="Failed to delete messages",
            errors={"detail": str(e)},
            request_id=request_id
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_online_users(request):
    request_id = getattr(request, 'id', None)
    
    try:
        unique_users = {}
        for channel_data in ChatConsumer.connected_users.values():
            user_id = channel_data['user_id']
            if user_id not in unique_users:
                unique_users[user_id] = channel_data['username']
        
        user_list = list(unique_users.values())
        
        logger.info(f"Online users retrieved | count={len(user_list)} | request_id={request_id}")
        
        return success_response(
            message="Online users retrieved successfully",
            data=user_list,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Error retrieving online users | error={str(e)} | request_id={request_id}")
        return error_response(
            message="Failed to retrieve online users",
            errors={"detail": str(e)},
            request_id=request_id
        )