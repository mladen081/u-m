# core/middleware.py

import uuid
import logging
from core.encryption import TokenEncryption

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.id = request_id
        
        logger.info(
            f"Request started | request_id={request_id} | {request.method} {request.path} | IP: {self.get_client_ip(request)}"
        )
        
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        
        logger.info(
            f"Request completed | request_id={request_id} | status={response.status_code}"
        )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DecryptTokenMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            
            if TokenEncryption.is_encrypted(token):
                try:
                    decrypted = TokenEncryption.decrypt(token)
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {decrypted}'
                except:
                    pass
        
        return self.get_response(request)