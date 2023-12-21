from pkg_resources import require
from rest_framework import serializers
from .models import RecruitmentPost
from schedules.models import Schedule
from teams.models import Team

class RecruitmentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentPost
        fields = ['id', 'team', 'author', 'title', 'content', 'region', 'created_at', 'updated_at', 'view_count']

class RecruitmentPostCreateSerializer(serializers.Serializer):
    # 게시글 필수 파라미터
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    # 게시글 옵션 파라미터
    region = serializers.CharField(required=False)
    # 팀 모델 관련 필수 파라미터
    category = serializers.CharField(required=True)
    max_attendance = serializers.IntegerField(required=True)
    # 팀 지정 옵션 파라미터
    team_id = serializers.IntegerField(required=True)
    # 일정 모델 관련 옵션 파라미터
    frequency = serializers.CharField(required=False)
    week = serializers.CharField(required=False)
    day = serializers.CharField(required=False)

    # 읽기 전용 
    team = serializers.SerializerMethodField()

    def get_team(self, obj):
        if self.validated_data is None:
            return None
        team_id = self.validated_data.get('team_id')
        
        try: 
            return Team.objects.get(id=team_id)
        except Exception as e:
            return None
    