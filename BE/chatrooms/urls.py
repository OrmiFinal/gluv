from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter(trailing_slash=True)
router.register(r'', views.ChatRoomListView, basename='stocks')

urlpatterns = [
    path("test/", views.chatroom_test, name="chatroom_test_index"),
    path('',  include(router.urls)),
]
