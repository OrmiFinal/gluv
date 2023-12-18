from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularJSONAPIView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include("main.urls")),
    path('books/', include("books.urls")),
    # path('chatrooms/', include("chatrooms.urls")),
    # path('comments/', include("comments.urls")),
    # path('likes/', include("likes.urls")),
    # path('messages/', include("messages.urls")),
    # path('notifications/', include("notifications.urls")),
    path('posts/', include("posts.urls")),
    # path('recruits/', include("recruits.urls")),
    # path('reports/', include("reports.urls")),
    # path('schedules/', include("schedules.urls")),
    # path('teams/', include("teams.urls")),
    path('users/', include("users.urls")),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 토큰발급/재생성
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), # 토큰 검증
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Spectacular Document App Name
app_name = 'api'

# Spectacular Document API
urlpatterns += [
    path("docs/json/", SpectacularJSONAPIView.as_view(), name="schema-json"),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema-json'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema-json'), name='redoc'),
]
