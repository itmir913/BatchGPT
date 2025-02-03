import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class TaskStatusConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    async def connect(self):
        """ 클라이언트가 WebSocket에 연결할 때 호출 """
        await self.accept()
        self.batch_id = None
        self.task_units = set()

    async def disconnect(self, close_code):
        """ 클라이언트가 WebSocket을 종료할 때 호출 """
        if self.batch_id:
            await self.channel_layer.group_discard(f"batch_{self.batch_id}", self.channel_name)
            print(f"Batch job with ID {self.batch_id} stopped subscribe")

    async def receive(self, text_data=None, bytes_data=None):
        """ 클라이언트에서 메시지를 받았을 때 호출 """
        data = json.loads(text_data)
        self.batch_id = str(data.get("batch_id"))
        self.task_units = set(data.get("task_units", []))

        await self.channel_layer.group_add(f"batch_{self.batch_id}", self.channel_name)
        logger.debug(f"Batch job with ID {self.batch_id} started subscribe: {self.task_units}")

    async def task_status(self, event):
        """ 특정 TaskUnit이 완료되었을 때, 구독 중인 클라이언트에게 알림 전송 """
        task_unit_id = event["task_unit_id"]

        if task_unit_id in self.task_units:
            logger.debug(f"API: task_status {task_unit_id} sent to clients !!!!!!")
            await self.send(text_data=json.dumps({
                "batch_id": event["batch_id"],
                "task_unit_id": task_unit_id,
                "status": event["status"],
                "result": event["result"],
            }))
            self.task_units.remove(task_unit_id)
