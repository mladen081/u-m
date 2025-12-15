# core/middleware.py

import uuid
import logging

from django.conf import settings

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

class SecurityHeadersMiddleware:
    """
    Dodaje security headers na svaki response
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        ws_url = 'ws://localhost:8000' if settings.DEBUG else 'wss://mladenapp.duckdns.org'
        
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            f"connect-src 'self' {ws_url}; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response