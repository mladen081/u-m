# core/responses.py

from http import HTTPStatus
from typing import Any, Dict, Optional, Union
from rest_framework.response import Response


def _build_body(
    status_str: str,
    message: str,
    payload: Optional[Union[Dict, list]] = None,
    code: Optional[str] = None,
    meta: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper that creates the basic response structure
    Always includes data/errors key for consistency
    
    Args:
        status_str: "success" or "error"
        message: Human-readable message
        payload: Data for success, errors for error responses
        code: Machine-readable error code (e.g., "VALIDATION_ERROR")
        meta: Metadata (pagination, timestamps, etc.)
        request_id: Unique request identifier for debugging
    """
    body = {
        "status": status_str,
        "message": message,
    }
    
    # Add request_id if available (for debugging)
    if request_id:
        body["request_id"] = request_id
    
    # Add code if provided (useful for frontend error handling)
    if code:
        body["code"] = code
    
    # Always include data or errors key with empty dict as default
    key = "data" if status_str == "success" else "errors"
    body[key] = payload if payload is not None else {}
    
    # Add meta if provided (pagination, etc.)
    if meta:
        body["meta"] = meta
    
    return body


def _get_request_id(context=None):
    """Extract request ID from context if available"""
    if context and 'request' in context:
        return getattr(context['request'], 'id', None)
    return None


# ==================== SUCCESS RESPONSES ====================

def success_response(
    message: str = "Success",
    data: Optional[Union[Dict, list]] = None,
    status: HTTPStatus = HTTPStatus.OK,
    meta: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    Standard success response
    
    Args:
        message: Success message
        data: Response payload
        status: HTTP status code (200, 201, etc.)
        meta: Optional metadata (pagination, etc.)
        request_id: Optional request ID for tracking
    
    Example:
        success_response("User retrieved", data={"id": 1, "name": "John"})
    """
    body = _build_body("success", message, data, meta=meta, request_id=request_id)
    response = Response(body, status=status)
    if request_id:
        response['X-Request-ID'] = request_id
    return response


def created_response(
    message: str = "Resource created successfully",
    data: Optional[Union[Dict, list]] = None,
    meta: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    201 Created response
    Use when new resource is created
    
    Example:
        created_response("User created", data={"id": 1})
    """
    body = _build_body("success", message, data, meta=meta, request_id=request_id)
    response = Response(body, status=HTTPStatus.CREATED)
    if request_id:
        response['X-Request-ID'] = request_id
    return response


# ==================== ERROR RESPONSES ====================

def error_response(
    message: str = "Error occurred",
    errors: Optional[Union[Dict, list]] = None,
    status: HTTPStatus = HTTPStatus.BAD_REQUEST,
    code: Optional[str] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    Standard error response
    
    Args:
        message: Error message
        errors: Error details (validation errors, etc.)
        status: HTTP status code
        code: Machine-readable error code
        request_id: Optional request ID for tracking
    
    Example:
        error_response("Invalid data", errors={"email": ["Invalid format"]}, code="VALIDATION_ERROR")
    """
    body = _build_body("error", message, errors, code=code, request_id=request_id)
    response = Response(body, status=status)
    if request_id:
        response['X-Request-ID'] = request_id
    return response


# ==================== COMMON ERROR SHORTCUTS ====================

def validation_error_response(
    errors: Optional[Union[Dict, list]] = None,
    message: str = "Validation failed",
    request_id: Optional[str] = None
) -> Response:
    """
    400 Bad Request - Validation errors
    
    Example:
        validation_error_response({"email": ["This field is required"]})
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.BAD_REQUEST,
        code="VALIDATION_ERROR",
        request_id=request_id
    )


def unauthorized_response(
    message: str = "Authentication required",
    errors: Optional[Union[Dict, list]] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    401 Unauthorized - Authentication missing or invalid
    
    Example:
        unauthorized_response("Invalid token")
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.UNAUTHORIZED,
        code="UNAUTHORIZED",
        request_id=request_id
    )


def forbidden_response(
    message: str = "Permission denied",
    errors: Optional[Union[Dict, list]] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    403 Forbidden - Authenticated but no permission
    
    Example:
        forbidden_response("Admin access required")
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.FORBIDDEN,
        code="FORBIDDEN",
        request_id=request_id
    )


def not_found_response(
    message: str = "Resource not found",
    errors: Optional[Union[Dict, list]] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    404 Not Found
    
    Example:
        not_found_response("User with id 123 not found")
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.NOT_FOUND,
        code="NOT_FOUND",
        request_id=request_id
    )


def conflict_response(
    message: str = "Resource already exists",
    errors: Optional[Union[Dict, list]] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    409 Conflict - Resource conflict (e.g., duplicate email)
    
    Example:
        conflict_response("Email already registered")
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.CONFLICT,
        code="CONFLICT",
        request_id=request_id
    )


def server_error_response(
    message: str = "Internal server error",
    errors: Optional[Union[Dict, list]] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    500 Internal Server Error
    
    Example:
        server_error_response("Database connection failed")
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        code="SERVER_ERROR",
        request_id=request_id
    )


def rate_limit_response(
    message: str = "Too many requests",
    errors: Optional[Union[Dict, list]] = None,
    request_id: Optional[str] = None
) -> Response:
    """
    429 Too Many Requests - Rate limiting
    
    Example:
        rate_limit_response("Try again in 60 seconds")
    """
    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.TOO_MANY_REQUESTS,
        code="RATE_LIMIT_EXCEEDED",
        request_id=request_id
    )