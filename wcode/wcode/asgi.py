import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import wcode.routing  # Make sure to import your routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wcode.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                wcode.routing.websocket_urlpatterns  # Reference the websocket routes here
            )
        )
    ),
})
