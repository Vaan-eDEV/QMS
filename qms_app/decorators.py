from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def require_page_permission(permission_field):

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Superuser always allowed
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            access = getattr(request.user, "page_access", None)

            if not access:
                return redirect("denied")

            if not getattr(access, permission_field, False):
                return redirect("denied")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
