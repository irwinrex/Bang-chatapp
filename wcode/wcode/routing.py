from django.urls import path
from chat.consumers import ChatConsumer  # Replace with your actual app name

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),  # Dynamic room name
]
