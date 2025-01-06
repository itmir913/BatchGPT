# tasks/celery.py
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Django settings 파일을 Celery에 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('tasks')

# Django의 settings.py에서 Celery 설정을 가져옵니다.
app.conf.broker_connection_retry_on_startup = True
app.config_from_object('django.conf:settings', namespace='CELERY')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Celery가 시작된 후, 자동으로 작업 실행
    from .task_queue import resume_pending_tasks
    resume_pending_tasks.apply_async()


# Celery 작업 자동 발견
app.autodiscover_tasks()

# sudo apt install redis-server
# sudo service redis-server start
