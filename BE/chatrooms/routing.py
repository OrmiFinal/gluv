from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("chatrooms/<int:room_id>/", consumers.ChatRoomConsumer.as_asgi()),
]
