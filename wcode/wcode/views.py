from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

def health_check(request):
    # You can add additional checks here if needed
    status = {
        'status': 'ok',
        'message': 'Application is healthy'
    }
    return JsonResponse(status)

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
