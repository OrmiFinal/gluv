from django.views.generic import ListView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from chatrooms.serializers import ChatRoomSerializer, ListResponseSerializer
from chatrooms.models import ChatRoom

class ChatRoomTestListView(ListView):
    '''
    테스트용 ListView
    '''
    model = ChatRoom

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.all()
        return qs

chatroom_test = ChatRoomTestListView.as_view()


class ChatRoomListView(viewsets.ViewSet):
    '''
    입장 가능한 채팅방 조회
    '''
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=None)
        
        chat_rooms = ChatRoom.objects.filter(team__members=user)
        
        response_serializer = ListResponseSerializer(data={
            'status': 'success',
            'message': 'Success message',
            'data': ChatRoomSerializer(chat_rooms, many=True).data
        })
        response_serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=response_serializer.validated_data)