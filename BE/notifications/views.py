from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework import status
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from notifications.serializers import NotificationSerializer, ReadNotificationSerializer
from notifications.models import Notification


class NotificationPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, status, message, data):
        return Response({
            'status': 'success',
            'message': 'Success message',
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

@extend_schema_view(
    read=extend_schema(
        responses={status.HTTP_200_OK: NotificationSerializer(many=True)},
        request=ReadNotificationSerializer(),
    )
)
class NotificationView(viewsets.ViewSet):
    '''
    알림 관련 ViewSet
    '''

    def get_permissions(self):
        return [IsAuthenticated()]
    
    def generate_response(self, status, message, data=None):
        return {
            'status': status,
            'message': message,
            'data': data,
        }
    
    
    @action(methods=["get"], detail=False, url_path='unread', url_name="unread")
    def unread(self, request, *args, **kwargs):
        '''
        알림 조회
        '''

        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        data = NotificationSerializer(notifications, many=True).data
        print(data)
        response = self.generate_response(
            status='success', 
            message='성공적으로 읽지 않은 알림을 반환했습니다.', 
            data=data)
        return Response(status=status.HTTP_200_OK, data=response)
    
    @action(methods=["patch"], detail=False, url_path='read', url_name="read")
    def read(self, request, *args, **kwargs):
        '''
        읽음 표시 등 알림의 상태를 변경하는 API
        '''

        # 알림 ID 리스트 파싱
        notification_ids = request.data.get('ids', [])

        notifications = Notification.objects.filter(user=request.user, id__in=notification_ids)
        if notifications.exists() == False:
            response = self.generate_response(
                status='error',
                message='선택한 알림을 찾을 수 없습니다.',
            )
            return Response(status=status.HTTP_404_NOT_FOUND, data=response)
        
        notifications.update(is_read=True)
        data = NotificationSerializer(notifications, many=True).data
        response = self.generate_response(
            status='success',
            message='성공적으로 알림 수신 확인했습니다.',
            data=data
        )
        return Response(status=status.HTTP_200_OK, data=response)
    

    def list(self, request, *args, **kwargs):
        '''
        전체 알림 조회
        '''

        user = request.user
        paginator = NotificationPagination()

        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(status='success', message='Successfully', data=serializer.data)
