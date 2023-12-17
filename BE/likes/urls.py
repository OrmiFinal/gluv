from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LikeViewSet

router = DefaultRouter()
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = [
    # 다른 URL 패턴들...
    path('api/', include(router.urls)),
    # 다른 URL 패턴들...
]
