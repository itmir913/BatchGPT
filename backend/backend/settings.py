"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8g4(1o%l!dz7u@&v++ktyf4s@@&p#li0d3#$ryt*7k$0^#7ooq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
    'users',
    'tasks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'dist')],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'dist/')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 기존 로거 비활성화 여부
    'formatters': {  # 로그 메시지 형식 정의
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {  # 로그 처리 방식 정의
        'console': {
            'level': 'DEBUG',  # 콘솔에 출력할 최소 로그 레벨
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',  # 사용할 포맷터
        },
    },
    'loggers': {  # 로거 정의
        'django': {
            'handlers': ['console'],  # 핸들러 연결
            'level': 'INFO',  # 최소 로그 레벨
            'propagate': True,  # 상위 로거로 전파 여부
        },
    },
}

# Vue.js의 로컬 개발 서버 정규식을 사용하여 허용
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',  # Vue.js 개발 서버
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",  # localhost의 모든 포트를 허용
]
CORS_ALLOW_CREDENTIALS = True

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis 브로커 URL
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # 작업 결과를 Redis에 저장
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'resume_pending_task_units': {
        'task': 'tasks.resume_queue.resume_pending_tasks_task_units',  # 작업 이름
        'schedule': crontab(minute='*/5'),  # 5분마다 실행
    },
    'resume_pending_batch_jobs': {
        'task': 'tasks.resume_queue.resume_pending_tasks_batch_job',  # 작업 이름
        'schedule': crontab(minute='*/5'),  # 5분마다 실행
    },
}

# load env
ENV_PATH = os.path.join(BASE_DIR, '.env')
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Pagination
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 한 페이지에 표시할 데이터 개수
}
