# tasks/queue_task_units.py
import json
import time

from celery import shared_task
from django.db.models import Q
from openai import OpenAI

from api.models import BatchJob
from backend.settings import OPENAI_API_KEY


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_task_unit(self, task_unit_id):
    # ImportError: cannot import name 'TaskUnit' from partially initialized module 'api.models' (most likely due to a circular import)
    from api.models import TaskUnit, TaskUnitResponse, TaskUnitStatus

    try:
        start_time = time.time()

        task_unit = TaskUnit.objects.get(id=task_unit_id)
        if task_unit.task_unit_status == TaskUnitStatus.COMPLETED:
            return

        task_unit.set_status(TaskUnitStatus.IN_PROGRESS)
        task_unit.save()

        batch_job = BatchJob.objects.get(id=task_unit.batch_job_id)
        batch_job_config = batch_job.configs or {}
        model = batch_job_config['gpt_model']

        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": task_unit.text_data,
                    }
                ],
                max_tokens=500
            )

            # chatgpt_reply = response.choices[0].message.content
            task_unit_response = TaskUnitResponse.objects.create(
                task_unit=task_unit,
                task_response_status=TaskUnitStatus.COMPLETED,
                request_data=task_unit.text_data,
                response_data=response.model_dump_json() if isinstance(response.model_dump_json(),
                                                                       dict) else json.loads(
                    response.model_dump_json()),
            )

            task_unit_response.processing_time = calculate_processing_time(start_time)
            task_unit_response.save()

            task_unit.set_status(TaskUnitStatus.COMPLETED)
            task_unit.save()

        except Exception as e:
            # 예외 처리: 요청 실패 및 오류 발생 시 처리
            task_unit_response = TaskUnitResponse.objects.create(
                task_unit=task_unit,
                task_response_status=TaskUnitStatus.FAILED,
                request_data=task_unit.text_data,
                error_code="500",  # 예시로 500번 에러 코드
                error_message=str(e),
            )

            task_unit_response.processing_time = calculate_processing_time(start_time)
            task_unit_response.save()

            task_unit.set_status(TaskUnitStatus.FAILED)
            task_unit.save()

            raise self.retry(exc=e, countdown=1)

    except TaskUnit.DoesNotExist as e:
        pass


@shared_task
def resume_pending_tasks():
    from api.models import TaskUnit, TaskUnitStatus
    pending_or_in_progress_tasks = TaskUnit.objects.filter(
        Q(task_unit_status=TaskUnitStatus.PENDING) | Q(task_unit_status=TaskUnitStatus.IN_PROGRESS)
    )
    for task in pending_or_in_progress_tasks:
        process_task_unit.apply_async(args=[task.id])


def calculate_processing_time(start_time):
    """작업 시간 계산 후 저장"""
    end_time = time.time()
    return end_time - start_time
