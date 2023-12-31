from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    '''
    커스텀 유저 매니저
    '''
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    '''
    커스텀 유저 모델
    Detail:
        username을 email로 대체
    '''
    REGION_CHOICES = [
        ('서울', '서울'),
        ('경기', '경기'),
        ('충남', '충남'),
        ('충북', '충북'),
        ('강원', '강원'),
        ('전남', '전남'),
        ('전북', '전북'),
        ('경북', '경북'),
        ('경남', '경남'),
        ('제주', '제주'),
    ]

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, blank=True)
    nickname = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='%Y%m%d/', null=True, blank=True)
    profile_content = models.TextField(blank=True)
    is_blocked = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email
