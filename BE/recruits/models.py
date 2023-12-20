from django.db import models
from django.contrib.auth import get_user_model
from teams.models import Team

class RecruitmentPost(models.Model):
    '''
    모집 게시글 모델

    Detail:
        모집 게시글 작성에 필요한 Category와 같은 정보는 외래키로 설정한 Team 모델에서 가져옵니다.
        - Category, max_attendance, current_attendance
    '''
    REGION_CHOICES = [
        ('지역 무관', '지역 무관'),
        ('서울', '서울'),
        ('경기', '경기'),
        ('강원', '강원'),
        ('충북', '충북'),
        ('충북', '충남'),
        ('전북', '전북'),
        ('전남', '전남'),
        ('경북', '경북'),
        ('경남', '경남'),
        ('제주', '제주'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    region = models.CharField(max_length=10, choices=REGION_CHOICES, default='지역 무관')

    def __str__(self):
        return self.title
