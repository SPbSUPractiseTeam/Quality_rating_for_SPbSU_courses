from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from .consumers import CourseConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("notifications/", CourseConsumer),
    ])
})