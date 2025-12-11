# chat/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core.responses import success_response
from .models import Message
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
        from core.responses import error_response
        return error_response(
            message="Failed to retrieve messages",
            errors={"detail": str(e)},
            request_id=request_id
        )