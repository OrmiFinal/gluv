from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter(trailing_slash=True)
router.register(r'', views.CommunityPostView, basename='posts')

urlpatterns = [
    path('',  include(router.urls)),
]
