class HeartbeatCsrfExemptMiddleware:
    """
    Middleware que exime de la verificación CSRF solo a las rutas de heartbeat.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Eximir de CSRF solo las rutas específicas de heartbeat
        if request.path.endswith('/raw/heartbeat/') or request.path.endswith('/simple/heartbeat/'):
            request._dont_enforce_csrf_checks = True
        
        response = self.get_response(request)
        return response