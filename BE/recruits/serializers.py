from rest_framework import serializers
from .models import RecruitmentPost
from schedules.models import Schedule
from teams.models import Team

class RecruitmentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentPost
        fields = ['id', 'team', 'author', 'title', 'content', 'region', 'created_at', 'updated_at', 'view_count']


class RecruitmentPostCreateSerializer(serializers.ModelSerializer):
    frequency = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()

    category = serializers.SerializerMethodField()
    max_attendance = serializers.SerializerMethodField()

    class Meta:
        model = RecruitmentPost
        fields = ['team', 'title', 'content', 'region', 'frequency', 'week', 'day', 'category', 'max_attendance']
    
    def get_frequency(self, obj):
        team_id = self.context.get('team_id')
        schedule = Schedule.objects.filter(team_id=team_id).first()
        return schedule.frequency if schedule else None

    def get_day(self, obj):
        team_id = self.context.get('team_id')
        schedule = Schedule.objects.filter(team_id=team_id).first()
        return schedule.day if schedule else None

    def get_week(self, obj):
        team_id = self.context.get('team_id')
        schedule = Schedule.objects.filter(team_id=team_id).first()
        return schedule.week if schedule else None

    def get_category(self, obj):
        team_id = self.context.get('team_id')
        team = Team.objects.filter(team_id=team_id).first()
        return team.category if team else None
    
    def get_max_attendance(self, obj):
        team_id = self.context.get('team_id')
        team = Team.objects.filter(team_id=team_id).first()
        return team.max_attendance if team else None
