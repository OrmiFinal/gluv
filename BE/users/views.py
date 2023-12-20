from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import User
from .serializers import UserSerializer, UserEditSerializer
from .permissions import IsOwner

class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password1 = form.cleaned_data.get('password1')
        password2 = form.cleaned_data.get('password2')
        nickname = form.cleaned_data.get('nickname')
        return super().form_valid(form)

class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except PermissionDenied:
            return Response({"detail": "로그인 해야 볼 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

class UserProfileEditView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserEditSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        try:
            self.check_object_permissions(request, self.get_object())
            serializer = self.get_serializer(self.get_object(), data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(instance=self.get_object()).data)
        except (PermissionDenied, ValidationError) as e:
            if isinstance(e, PermissionDenied):
                return Response({"detail": "로그인 한 본인의 정보만 접근 및 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            self.check_object_permissions(request, self.get_object())
            serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(instance=self.get_object()).data)
        except (PermissionDenied, ValidationError) as e:
            if isinstance(e, PermissionDenied):
                return Response({"detail": "로그인 한 본인의 정보만 접근 및 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateView(DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("로그인이 필요합니다.")
        instance = self.get_object()
        instance.delete()
        response_data = {'detail': '성공적으로 탈퇴되었습니다.'}
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh', None)
            if refresh_token:
                RefreshToken(refresh_token).blacklist()

            response_data = {'detail': '성공적으로 로그아웃되었습니다.'}
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {'detail': '로그아웃하는 데 실패했습니다.'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)