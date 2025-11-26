# accounts/decorators.py

from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from core.responses import forbidden_response


def admin_required(view_func):
    """
    Decorator that checks if user is authenticated and has admin role.
    Use for function-based views.
    
    Example:
        @admin_required
        def my_admin_view(request):
            return JsonResponse({"message": "Admin only"})
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            return forbidden_response(
                message="Admin access required",
                request_id=getattr(request, 'id', None)
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """
    Decorator that checks if user has one of the allowed roles.
    
    Example:
        @role_required('admin', 'user')
        def my_view(request):
            return JsonResponse({"message": "Access granted"})
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return forbidden_response(
                    message=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                    request_id=getattr(request, 'id', None)
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator