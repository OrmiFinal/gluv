from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    UserCreateView,
    UserDetailView,
    UserProfileEditView,
    UserDeactivateView,
    UserLogoutView,
)

urlpatterns = [
    path('signup/', UserCreateView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('<int:pk>/profile/', UserDetailView.as_view(), name='user_detail'),
    path('profile/', UserProfileEditView.as_view(), name='user_profile_edit'),
    path('deactivate/', UserDeactivateView.as_view(), name='user_deactivate'),
]
