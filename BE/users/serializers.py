from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'created_at', 'region', 'nickname', 'profile_image', 'profile_content', 'is_blocked')
        # extra_kwargs = {'password': {'write_only': True, 'style': {'input_type': 'password'}}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('region', 'nickname', 'profile_image', 'profile_content')
