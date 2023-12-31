import os
from datetime import timedelta
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab
from urllib.parse import quote

# BASE DIR 설정
BASE_DIR = Path(__file__).resolve().parent.parent
# .env 불러오기
load_dotenv(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG")

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # install app
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    # custom app
    'chatrooms',
    'comments',
    'likes',
    'chatroom_messages',
    'notifications',
    'posts',
    'recruits',
    'reports',
    'schedules',
    'teams',
    'users',
    'books',
    # Channels
    'channels',
    # Celery Task
    'django_celery_beat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gluv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gluv.wsgi.application'
ASGI_APPLICATION = 'gluv.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST framework 설정
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Media 설정
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# JWT 설정
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# 커스텀 User 모델 설정
AUTH_USER_MODEL = 'users.User'

# 환경 변수에서 Redis 비밀번호 조회
REDIS_KEY = os.getenv("REDIS_KEY", "")

# Django Channels 설정
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [f'redis://:{quote(REDIS_KEY)}@localhost:6379/0'],
        },
    },
}

# CORS ORIGIN 허용할 주소
CORS_ORIGIN_WHITELIST = ['http://127.0.0.1:3001', 'http://localhost:3001']
CORS_ALLOW_CREDENTIALS = True

# Spectacular 설정
SPECTACULAR_SETTINGS = {
    'TITLE': 'drf-spectacular API Document',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'SECURITY_DEFINITIONS': {
            'Token': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
            },
        },
        'persistAuthorization': True,
    },
}

REDIS_KEY = os.getenv("REDIS_KEY")

# Celery Broker URL과 Result Backend URL
CELERY_BROKER_URL = f'redis://:{quote(REDIS_KEY)}@localhost:6379/0'
CELERY_RESULT_BACKEND = f'redis://:{quote(REDIS_KEY)}@localhost:6379/0'

# Celery 메시지 형식 지정
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Celery Beat Task 스케줄 설정
# 1분마다 books.tasks.fetch_recent_book 실행
CELERY_BEAT_SCHEDULE = {
    'fetch_recent_book': {
        'task': 'books.tasks.fetch_recent_book',
        'schedule': timedelta(minutes=1),
    },
}
