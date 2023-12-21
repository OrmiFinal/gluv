from email.policy import default
from django.db import models
from teams.models import Team


class Schedule(models.Model):
    '''
    일정 모델

    Attributes:
        team (ForeignKey): Team 모델과의 1:1 관계
        frequency : 매일, 매주, 매월과 같은 반복성을 설정합니다. 특정일만 진행할 모임일 경우 '주기없음'으로 설정합니다.
        day : frequency를 '매주' 혹은 '매달'로 설정했을 때, 'x요일'을 지정할 때 사용합니다.
        week : frequency를 '매달'로 설정했을 때, 'n번째' 주를 특정하기 위해 사용합니다.
    
    Detail:
        FE에서 day, week를 다중값으로 받았을 때 list형태로 data를 주고받습니다.
        list로 날아온 data를 변형하여 DB에는 "월요일, 수요일"로 저장합니다.
    '''
    FREQUENCY_CHOICES = [
        ('주기없음', '주기없음'),
        ('매일', '매일'),
        ('매주', '매주'),
        ('매월', '매월'),
    ]

    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='schedule')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, null=True,default="주기없음")
    day = models.CharField(max_length=100, null=True, blank=True)
    week = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.team}의 일정'
