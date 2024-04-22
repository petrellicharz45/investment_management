from .models import AccessLog

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        action = f"{request.method} - {request.path}"
        AccessLog.objects.create(user=user, action=action)

        return response
