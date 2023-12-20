from rest_framework import serializers
from django.db import transaction

from .models import Schedule

# class ScheduleSerializer(serializers.ModelSerializer):
#     '''
#     Schedule 모델에 대한 Serializer
#     '''
#     class Meta:
#         model = Schedule
#         fields = ['id', 'team', 'frequency', 'day', 'week', 'start_time', 'end_time']

class ScheduleSerializer(serializers.ModelSerializer):
    '''
    Schedule 모델에 대한 Serializer
    '''
    day = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    week = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    class Meta:
        model = Schedule
        fields = ['id', 'team', 'frequency', 'day', 'week', 'start_time', 'end_time']

class ChangeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['frequency', 'day', 'week', 'start_time', 'end_time']

    @transaction.atomic
    def update(self, instance, validated_data):
        fields_to_update = ['frequency', 'day', 'week', 'start_time', 'end_time']

        for field in fields_to_update:
            new_value = validated_data.get(field, getattr(instance, field))
            if new_value != getattr(instance, field):
                setattr(instance, field, new_value)

        instance.save()
        return instance
