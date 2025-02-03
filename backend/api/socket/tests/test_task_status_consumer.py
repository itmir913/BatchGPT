import asyncio

from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.test import TestCase

from backend.asgi import application


class TaskStatusConsumerTest(TestCase):
    """ 서버 측 WebSocket 처리 로직을 테스트 """

    async def test_notify_task_update(self):
        # WebSocket 커넥터
        communicator = WebsocketCommunicator(application, f"ws/task_status/")

        # WebSocket 연결
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # 구독 요청 메시지 전송
        subscribe_data = {
            "batch_id": "2",
            "task_units": [101, 102, 103]
        }
        await communicator.send_json_to(subscribe_data)

        # 그룹에 추가 후 1초 후에 메시지 전송
        await asyncio.sleep(1)

        # 여기서 group_send를 호출하여 실제로 메시지를 보내는 것
        channel_layer = get_channel_layer()

        # 예시로 전송할 메시지
        event_data = {
            "task_unit_id": 101,
            "batch_id": "2",
            "status": "completed",
            "result": "success"
        }

        # 서버 측에서 특정 TaskUnit 완료 알림을 보내는 로직 테스트
        await channel_layer.group_send(
            f"batch_{event_data['batch_id']}",
            {
                "type": "task_status",
                **event_data
            }
        )

        # 메시지를 수신하고 그 내용 확인
        response = await communicator.receive_json_from()
        print("Received response:", response)

        self.assertEqual(response["task_unit_id"], 101)
        self.assertEqual(response["status"], "completed")
        self.assertEqual(response["result"], "success")

        # WebSocket 연결 종료
        await communicator.disconnect()
