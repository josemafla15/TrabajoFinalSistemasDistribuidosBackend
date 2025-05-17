from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def csrf_exempt_view(view_func):
    """
    Decorador que asegura que una vista está exenta de CSRF.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        request._dont_enforce_csrf_checks = True
        return view_func(request, *args, **kwargs)
    return wrapped_view