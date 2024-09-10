from django.shortcuts import render
from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
# Create your views here.
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer