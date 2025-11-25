# core/exceptions.py

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    Throttled,
    ParseError,
    NotAcceptable,
    UnsupportedMediaType,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .responses import (
    validation_error_response,
    unauthorized_response,
    forbidden_response,
    not_found_response,
    server_error_response,
    rate_limit_response,
    error_response,
)
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all DRF exceptions
    using standardized response functions.
    
    Args:
        exc: The exception instance
        context: Dict with 'view' and 'request' keys
    
    Returns:
        Response object with standardized format
    """
    
    # Extract request ID if available
    request_id = None
    if context and 'request' in context:
        request_id = getattr(context['request'], 'id', None)
    
    # Call DRF's default handler first to get standard error response
    response = drf_exception_handler(exc, context)
    
    # If DRF handled it, format it with our custom responses
    if response is not None:
        
        # Validation errors (400)
        if isinstance(exc, ValidationError):
            return validation_error_response(
                errors=response.data,
                message="Validation failed",
                request_id=request_id
            )
        
        # Parse errors (400) - malformed JSON or data
        if isinstance(exc, ParseError):
            message = str(exc) if str(exc) else "Malformed request data"
            return error_response(
                message=message,
                errors=response.data if isinstance(response.data, dict) else None,
                status=response.status_code,
                code="PARSE_ERROR",
                request_id=request_id
            )
        
        # Authentication errors (401)
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            message = str(exc) if str(exc) else "Authentication required"
            return unauthorized_response(
                message=message,
                errors=response.data if isinstance(response.data, dict) else None,
                request_id=request_id
            )
        
        # Permission errors (403)
        if isinstance(exc, PermissionDenied):
            message = str(exc) if str(exc) else "Permission denied"
            return forbidden_response(
                message=message,
                errors=response.data if isinstance(response.data, dict) else None,
                request_id=request_id
            )
        
        # Not found errors (404)
        if isinstance(exc, (NotFound, Http404, ObjectDoesNotExist)):
            message = str(exc) if str(exc) else "Resource not found"
            return not_found_response(
                message=message,
                errors=response.data if isinstance(response.data, dict) else None,
                request_id=request_id
            )
        
        # Method not allowed (405)
        if isinstance(exc, MethodNotAllowed):
            return error_response(
                message=f"Method '{exc.method}' not allowed",
                errors=response.data if isinstance(response.data, dict) else None,
                status=response.status_code,
                code="METHOD_NOT_ALLOWED",
                request_id=request_id
            )
        
        # Not acceptable (406) - client requested unsupported format
        if isinstance(exc, NotAcceptable):
            return error_response(
                message="Requested format is not available",
                errors=response.data if isinstance(response.data, dict) else None,
                status=response.status_code,
                code="NOT_ACCEPTABLE",
                request_id=request_id
            )
        
        # Unsupported media type (415) - client sent unsupported content-type
        if isinstance(exc, UnsupportedMediaType):
            media_type = exc.detail if hasattr(exc, 'detail') else None
            return error_response(
                message=f"Unsupported media type: {media_type}" if media_type else "Unsupported media type",
                errors=response.data if isinstance(response.data, dict) else None,
                status=response.status_code,
                code="UNSUPPORTED_MEDIA_TYPE",
                request_id=request_id
            )
        
        # Rate limiting (429)
        if isinstance(exc, Throttled):
            wait_time = exc.wait if hasattr(exc, 'wait') else None
            message = f"Too many requests. Try again in {wait_time} seconds." if wait_time else "Too many requests"
            return rate_limit_response(
                message=message,
                errors={"wait": wait_time} if wait_time else None,
                request_id=request_id
            )
        
        # Generic DRF errors (fallback for any other APIException subclass)
        return error_response(
            message=str(exc) if str(exc) else "An error occurred",
            errors=response.data if isinstance(response.data, dict) else None,
            status=response.status_code,
            code="API_ERROR",
            request_id=request_id
        )
    
    # Non-DRF exceptions (500 errors)
    # Log the error for debugging
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            'context': context,
            'request_id': request_id
        }
    )
    
    # Return generic 500 error (don't expose internal details in production)
    return server_error_response(
        message="An unexpected error occurred",
        errors={"detail": str(exc)} if context.get('request') else None,
        request_id=request_id
    )