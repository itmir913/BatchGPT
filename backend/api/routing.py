from django.urls import re_path

from api.socket.task_status_consumer import TaskStatusConsumer

websocket_urlpatterns = [
    re_path(r"ws/task_status/", TaskStatusConsumer.as_asgi()),  # WebSocket URL 매핑
]
