from django.db import models
from teams.models import Team

class ChatRoom(models.Model):
    """
    실시간 채팅방 모델

    Attributes:
        team (ForeignKey): Team 모델과의 1:M 관계
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team}의 채팅방"