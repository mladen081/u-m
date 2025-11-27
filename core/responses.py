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

    body = {
        "status": status_str,
        "message": message,
    }
    
    if request_id:
        body["request_id"] = request_id
    
    if code:
        body["code"] = code
    
    key = "data" if status_str == "success" else "errors"
    body[key] = payload if payload is not None else {}
    
    if meta:
        body["meta"] = meta
    
    return body


def _get_request_id(context=None):
    if context and 'request' in context:
        return getattr(context['request'], 'id', None)
    return None

def success_response(
    message: str = "Success",
    data: Optional[Union[Dict, list]] = None,
    status: HTTPStatus = HTTPStatus.OK,
    meta: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> Response:

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

    body = _build_body("success", message, data, meta=meta, request_id=request_id)
    response = Response(body, status=HTTPStatus.CREATED)
    if request_id:
        response['X-Request-ID'] = request_id
    return response


def error_response(
    message: str = "Error occurred",
    errors: Optional[Union[Dict, list]] = None,
    status: HTTPStatus = HTTPStatus.BAD_REQUEST,
    code: Optional[str] = None,
    request_id: Optional[str] = None
) -> Response:

    body = _build_body("error", message, errors, code=code, request_id=request_id)
    response = Response(body, status=status)
    if request_id:
        response['X-Request-ID'] = request_id
    return response


def validation_error_response(
    errors: Optional[Union[Dict, list]] = None,
    message: str = "Validation failed",
    request_id: Optional[str] = None
) -> Response:

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

    return error_response(
        message=message,
        errors=errors,
        status=HTTPStatus.TOO_MANY_REQUESTS,
        code="RATE_LIMIT_EXCEEDED",
        request_id=request_id
    )