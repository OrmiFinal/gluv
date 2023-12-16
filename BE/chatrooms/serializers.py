from rest_framework import serializers

from .models import ChatRoom

class ListResponseSerializer(serializers.Serializer):
    '''
    일반적인 응답으로 포장하는 Serializer
    status : 응답 결과
    message : 응답 결과의 메시지
    data : 리스트 형태의 응답
    '''
    status = serializers.CharField()
    message = serializers.CharField()
    data = serializers.ListField(child=serializers.DictField(), required=False, allow_null=True, default=None)

class ChatRoomSerializer(serializers.ModelSerializer):
    '''
    ChatRoom 모델 Serializer
    '''
    class Meta:
        model = ChatRoom
        fields = '__all__'
