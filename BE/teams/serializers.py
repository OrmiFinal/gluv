from rest_framework import serializers
from chatrooms.models import ChatRoom

from schedules.models import Schedule
from recruits.models import RecruitmentPost
from .models import Team, TeamMember


class TeamSerializer(serializers.ModelSerializer):
    '''
    Team 모델 Serializer
    '''
    class Meta:
        model = Team
        fields = ['id', 'name', 'category', 'is_closed', 'location', 'max_attendance', 'current_attendance', 'introduce', 'image']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not instance.image:
            ret['image'] =  '/media/defalut_team.png'
        return ret

class TeamMemberSerializer(serializers.ModelSerializer):
    '''
    TeamMember 모델 Serializer
    '''
    nickname = serializers.SerializerMethodField()
    class Meta:
        model = TeamMember
        fields = ['user', 'nickname', 'team', 'is_leader', 'is_approved']

    def get_nickname(self, obj):
        '''
        닉네임 정보 제공
        '''
        return obj.user.nickname


class TeamMemberChangeSerializer(serializers.ModelSerializer):
    '''
    TeamMember 모델 수정을 위한 Serializer
    '''
    class Meta:
        model = TeamMember
        fields = ['user']


class TeamDetailSerializer(serializers.ModelSerializer):
    '''
    Team 모델 상세 조회를 위한 Serializer
    '''
    frequency = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    applied_member = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()
    recruit_id = serializers.SerializerMethodField()
    chatroom_id = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'category', 'is_closed', 'location', 'max_attendance', 'current_attendance', 'introduce', 'image',
            'applied_member', 'is_leader', 'frequency', 'day', 'week', 'start_time', 'end_time', 'recruit_id', 'chatroom_id',
        ]

    def get_related_data(self, obj):
        '''
        팀 상세 조회 시 필요한 데이터 조회
        '''
        team_id = self.context.get('team_id')
        user = self.context.get('user')

        team_member_data = TeamMember.objects.filter(team=obj, is_approved=False).count()
        is_leader = TeamMember.objects.filter(team=obj, user=user, is_leader=True).exists()
        schedule = Schedule.objects.filter(team_id=team_id).first()

        return {
            'applied_member_count': team_member_data,
            'is_leader': is_leader,
            'schedule': schedule,
        }

    def get_applied_member(self, obj):
        data = self.get_related_data(obj)
        return data['applied_member_count']

    def get_is_leader(self, obj):
        data = self.get_related_data(obj)
        return data['is_leader']

    def get_frequency(self, obj):
        data = self.get_related_data(obj)
        return data['schedule'].frequency if data['schedule'] else None

    def get_day(self, obj):
        data = self.get_related_data(obj)
        if not data['schedule']:
            return None
        
        return data['schedule'].day if data['schedule'].day is not None else None

    def get_week(self, obj):
        data = self.get_related_data(obj)
        if not data['schedule']:
            return None
        
        return data['schedule'].week if data['schedule'].week is not None else None

    def get_start_time(self, obj):
        data = self.get_related_data(obj)
        if not data['schedule']:
            return None
        
        return data['schedule'].start_time if data['schedule'].start_time is not None else None

    def get_end_time(self, obj):
        data = self.get_related_data(obj)
        if not data['schedule']:
            return None
        
        return data['schedule'].end_time if data['schedule'].end_time is not None else None
    
    def get_recruit_id(self, obj):
        exists = RecruitmentPost.objects.filter(team=obj).exists()
        if not exists:
            return None
        
        return RecruitmentPost.objects.filter(team=obj).first().id
    
    def get_chatroom_id(self, obj):
        exists = ChatRoom.objects.filter(team=obj).exists()
        if not exists:
            return None
        
        return ChatRoom.objects.filter(team=obj).first().id
    
    def get_location(self, obj):
        exists = RecruitmentPost.objects.filter(team=obj).exists()
        if not exists:
            return None
        
        return RecruitmentPost.objects.filter(team=obj).first().region