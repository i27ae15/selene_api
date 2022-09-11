from channels.routing import ProtocolTypeRouter

from channels.routing import ChannelNameRouter
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from django.urls import path
from chat.consumers import SeleneChat


application = ProtocolTypeRouter({
    'websocket':AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
            
            path('chat/testing/', SeleneChat())
            ])
        )
    )
})