import os
import environ
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from wcode.routing import websocket_urlpatterns  # Import your websocket URL patterns
from channels.security.websocket import AllowedHostsOriginValidator  # Optional for security

# Load environment variables
env = environ.Env()
environ.Env.read_env()  # Read .env file if present

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wcode.settings')  # Set the default settings module

# Initialize the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handle HTTP requests
    "websocket": AllowedHostsOriginValidator(  # Optional: Validates the origin of WebSocket connections
        AuthMiddlewareStack(  # Handle WebSocket connections with authentication
            URLRouter(
                websocket_urlpatterns  # Include your WebSocket URL patterns
            )
        )
    ),
})

