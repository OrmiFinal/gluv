import json
from channels.layers import get_channel_layer
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from chatroom_messages.models import ChatRoomMessage

from chatrooms.models import ChatRoom

User = get_user_model()

class OnlineUserManager:
    '''
    현재 접속자 관리자
    '''
    # 싱글톤 인스턴스
    _instance = None
    # 채팅 방과 현재 접속자 정보를 저장하고 있는 딕셔너리
    chat_rooms = {}

    def __new__(cls, chat_room_name):
        '''
        단일 인스턴스의 채팅방을 보장하기 위해 재정의함.

        Args:
        - cls: class 변수
        - chat_room_name: 채팅방 그룹 이름

        Returns:
        - 채팅방 그룹별 단일 인스턴스 반환

        Example:
        - OnlineUserManager('my_room_101')
        - OnlineUserManager('my_room_101').add_user('user_101')
        '''
        if chat_room_name not in cls.chat_rooms:
            cls.chat_rooms[chat_room_name] = super(OnlineUserManager, cls).__new__(cls)
            cls.chat_rooms[chat_room_name].online_users = set()
        return cls.chat_rooms[chat_room_name]

    def add_user(self, user_id):
        '''
        특정 채팅방에 접속자 추가

        Args:
        - user_id : 유저 ID
        '''
        self.online_users.add(user_id)

    def remove_user(self, user_id):
        '''
        특정 채팅방에 접속자 삭제

        Args:
        - user_id : 유저 ID
        '''
        self.online_users.discard(user_id)

    def get_online_users(self):
        '''
        특정 채팅방에 접속자 목록 조회

        Args:
        - user_id : 유저 ID

        Returns:
        - 접속자 목록 반환
        '''
        return list(self.online_users)

class ChatRoomConsumer(JsonWebsocketConsumer):
    # Django의 채널 레이어 객체를 가져옴
    # 이전에는 layer에 직접 접근하는 것이 가능했으나 현재는 불가능
    layer = get_channel_layer()
    # 채팅방 그룹 이름을 저장하는 변수
    room_group_name = None

    def connect(self):
        '''
        웹소켓 연결 시 호출되는 함수
        '''

        # 로그인된 사용자만 허용
        user = self.scope['user']
        print(user)
        if user.is_anonymous:
            self.close()
            return
    
        # 채팅방 접속 시도
        chat_room = self.get_chatroom()
        print(chat_room)
        if chat_room is None:
            self.close()
            return

        self.accept()
        self.room_group_name = f'chatroom_{chat_room.id}'
        #  실시간 유저에 등록
        self.add_user_to_group()
        self.fetch_previous_message()

    def disconnect(self, close_code):
        '''
        사용자의 연결이 끊겼을 때 호출되는 함수
        '''
        self.remove_user_to_group()

    def receive_json(self, content_dict, **kwargs):
        if content_dict['type'] == 'chat_message':
            room_id = self.scope["url_route"]["kwargs"]["room_id"]
            user_id = self.scope["user"].id

            # Impersonation 보안
            content_dict['sender'] = user_id

            chat_room = ChatRoom.objects.get(id=room_id)
            user = User.objects.get(id=user_id)
            
            # 채팅 메시지 저장
            _ = ChatRoomMessage.objects.create(content=content_dict['message'], chatroom=chat_room, user=user)

            # 채팅방으로 메시지 전송
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, content_dict
            )
    
    def chat_message(self, event):
        '''
        그룹에서 채팅 메시지를 받았을 때 호출되는 함수
        '''
        user_id = self.scope["user"].id

        message = event['message']
        sender = event['sender']

        # 메시지의 송신자를 제외한 메시지 전송  
        if sender != user_id:
            self.send(text_data=json.dumps({
                'message': message,
                'sender' : sender,
            }))

    def get_chatroom(self) -> ChatRoom | None:
        '''
        유저 ID와 채팅방 ID로 채팅방을 가져오는 함수
        퍼미션 확인 기능 수행
        '''
        try:
            user = self.scope['user']
            room_id = self.scope["url_route"]["kwargs"]["room_id"]
            return ChatRoom.objects.get(id=room_id, team__members=user)
        except Exception as e:
            print(e)
            return None
    
    def add_user_to_group(self):
        '''
        채팅방 그룹에 유저 추가
        '''
        user_id = self.scope["user"].id
        async_to_sync(self.layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        OnlineUserManager(self.room_group_name).add_user(user_id)
        self.refresh_online_users()
        self.send_server_message(f"{user_id} is connected")

    def remove_user_to_group(self):
        '''
        채팅방 그룹에 유저 제거
        '''
        if self.room_group_name is None:
            return
        
        user_id = self.scope["user"].id
        async_to_sync(self.layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        OnlineUserManager(self.room_group_name).remove_user(user_id)
        self.refresh_online_users()
        self.send_server_message(f"{user_id} is disconnected")

    def refresh_online_users(self):
        '''
        업데이트 된 현재 접속자 정보 제공
        '''
        online_users = OnlineUserManager(self.room_group_name).get_online_users()
        self.send_server_message(json.dumps({ "online_users" : online_users}))
    
    def fetch_previous_message(self):
        '''
        이전 대화 기록 조회
        '''
        room_id = self.scope["url_route"]["kwargs"]["room_id"]

        # 채팅방 객체 가져오기
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 이전 채팅 메시지 가져오기 (최근 10개만 가져오도록 설정)
        messages = ChatRoomMessage.objects.filter(chatroom=chat_room).order_by('-id')[:10]

        # 각 메시지를 클라이언트에 전송
        for message in reversed(messages):
            self.send_json({
                'type': 'chat_message',
                'message' : message.content,
                'sender': message.user.id,
            })

    def send_server_message(self, message):
        '''
        서버 메시지 전송
        '''
        async_to_sync(self.layer.group_send)(
            self.room_group_name, {
                'type': 'chat_message',
                'message': message,
                'sender': 'server',
            })
