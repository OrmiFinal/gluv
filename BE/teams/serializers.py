from rest_framework import serializers

from .models import Team, TeamMember
from schedules.models import Schedule


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'category', 'is_closed', 'location', 'max_attendance', 'current_attendance', 'introduce', 'image']


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['user', 'team', 'is_leader', 'is_approved']


class TeamMemberChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['user']

class TeamDetailSerializer(serializers.ModelSerializer):
    frequency = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    applied_member = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'name', 'category', 'is_closed', 'location', 'max_attendance', 'current_attendance', 'introduce', 'image',
            'applied_member', 'is_leader', 'frequency', 'day', 'week', 'start_time', 'end_time',
        ]

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
    
    def get_start_time(self, obj):
        team_id = self.context.get('team_id')
        schedule = Schedule.objects.filter(team_id=team_id).first()
        return schedule.start_time if schedule else None

    def get_end_time(self, obj):
        team_id = self.context.get('team_id')
        schedule = Schedule.objects.filter(team_id=team_id).first()
        return schedule.end_time if schedule else None
    
    def get_applied_member(self, obj):
        return TeamMember.objects.filter(team=obj, is_approved=False).count()

    def get_is_leader(self, obj):
        user = self.context.get('user')
        return TeamMember.objects.filter(team=obj, user=user, is_leader=True).exists()