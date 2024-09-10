from django.contrib.auth.models import User
from django.http import JsonResponse

def health_check(request):
    # You can add additional checks here if needed
    status = {
        'status': 'ok',
        'message': 'Application is healthy'
    }
    return JsonResponse(status)
