from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """Allows only admins (or superusers) to access the view."""
    @wraps(view_func)
    @login_required(login_url="dashboard:login")
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_admin_role):
            raise PermissionDenied("Administrator access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Allows any active staff member (admin OR operator)."""
    @wraps(view_func)
    @login_required(login_url="dashboard:login")
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff and request.user.is_active):
            raise PermissionDenied("Management access required.")
        return view_func(request, *args, **kwargs)
    return wrapper