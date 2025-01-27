# tasks/queue_task_units.py
import json
import logging
import time

from celery import shared_task
from openai import OpenAI

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_task_unit(self, task_unit_id):
    # ImportError: cannot import name 'TaskUnit' from partially initialized module 'api.models' (most likely due to a circular import)
    from django.core.cache import cache
    from django.shortcuts import get_object_or_404
    from api.models import TaskUnit, TaskUnitResponse, TaskUnitStatus, BatchJob
    from api.utils.cache_keys import task_unit_status_key
    from backend.settings import OPENAI_API_KEY

    try:
        start_time = time.time()

        task_unit = get_object_or_404(TaskUnit, id=task_unit_id)
        if task_unit.task_unit_status in [TaskUnitStatus.COMPLETED, TaskUnitStatus.FAILED]:
            cache.set(task_unit_status_key(task_unit_id), TaskUnitStatus.COMPLETED, timeout=30)
            logger.log(logging.INFO, f"Celery: The task with ID {task_unit_id} has already been completed.")
            return

        cache.set(task_unit_status_key(task_unit_id), TaskUnitStatus.IN_PROGRESS, timeout=30)
        task_unit.set_status(TaskUnitStatus.IN_PROGRESS)
        task_unit.save()

        batch_job = get_object_or_404(BatchJob, id=task_unit.batch_job_id)
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

            task_unit_response = TaskUnitResponse.objects.create(
                task_unit=task_unit,
                task_response_status=TaskUnitStatus.COMPLETED,
                request_data=task_unit.text_data,
                response_data=response.model_dump_json() if isinstance(response.model_dump_json(),
                                                                       dict) else json.loads(
                    response.model_dump_json()),
                processing_time=calculate_processing_time(start_time)
            )

            task_unit.set_status(TaskUnitStatus.COMPLETED)
            task_unit.latest_response = task_unit_response
            task_unit.save()

            cache.set(task_unit_status_key(task_unit_id), TaskUnitStatus.COMPLETED, timeout=30)
            logger.log(logging.INFO, f"Celery: The request for {task_unit_id} has been completed.")

        except Exception as e:
            # 예외 처리: 요청 실패 및 오류 발생 시 처리
            task_unit_response = TaskUnitResponse.objects.create(
                task_unit=task_unit,
                task_response_status=TaskUnitStatus.FAILED,
                request_data=task_unit.text_data,
                error_message=str(e),
                processing_time=calculate_processing_time(start_time),
            )

            task_unit.set_status(TaskUnitStatus.FAILED)
            task_unit.latest_response = task_unit_response
            task_unit.save()

            cache.set(task_unit_status_key(task_unit_id), TaskUnitStatus.FAILED, timeout=30)
            logger.log(logging.INFO,
                       f"Celery: The request for {task_unit_id} has failed for the following reason: {str(e)}")

            raise self.retry(exc=e, countdown=1)

    except TaskUnit.DoesNotExist as e:
        return


@shared_task
def resume_pending_tasks():
    from api.models import TaskUnit, TaskUnitStatus

    pending_or_in_progress_tasks = TaskUnit.objects.filter(task_unit_status=TaskUnitStatus.PENDING)
    for task in pending_or_in_progress_tasks:
        logger.log(logging.INFO,
                   f"Celery: Pending task {task.id} has been recognized and is now starting.")
        process_task_unit.apply_async(args=[task.id])


def calculate_processing_time(start_time):
    """작업 시간 계산 후 저장"""
    end_time = time.time()
    return end_time - start_time
