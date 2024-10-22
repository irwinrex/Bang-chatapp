# chat/urls.py

from django.urls import path
from .views import authenticate_and_create_chatroom

urlpatterns = [
    # Endpoint for creating a chatroom with authentication via JWT
    path('create-chatroom/', authenticate_and_create_chatroom, name='create-chatroom'),
]
