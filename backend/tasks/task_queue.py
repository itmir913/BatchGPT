# tasks/task_queue.py
import time

import requests
from celery import shared_task
from django.db.models import Q

URL = "https://google.com"


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_task_unit(self, task_unit_id):
    # ImportError: cannot import name 'TaskUnit' from partially initialized module 'api.models' (most likely due to a circular import)
    from api.models import TaskUnit, TaskUnitResponse, TaskUnitStatus

    try:
        start_time = time.time()
        task_unit = TaskUnit.objects.get(id=task_unit_id)
        task_unit.set_status(TaskUnitStatus.IN_PROGRESS)

        try:
            connect_timeout, read_timeout = 5.0, 30.0
            response = requests.get(URL, timeout=(connect_timeout, read_timeout))

            if response.status_code == 200:
                task_unit_response = TaskUnitResponse.objects.create(
                    task_unit=task_unit,
                    status=TaskUnitStatus.COMPLETED,
                    request_data=task_unit.text_data,
                    response_data=response.json(),
                )
                calculate_and_save_processing_time(task_unit_response, start_time)
                task_unit.set_status(TaskUnitStatus.COMPLETED)

            else:
                task_unit_response = TaskUnitResponse.objects.create(
                    task_unit=task_unit,
                    status=TaskUnitStatus.FAILED,
                    request_data=task_unit.text_data,
                    error_code=str(response.status_code),
                    error_message=response.text,
                )
                calculate_and_save_processing_time(task_unit_response, start_time)
                task_unit.set_status(TaskUnitStatus.FAILED)

                self.retry(countdown=1)

        except Exception as e:
            # 예외 처리: 요청 실패 및 오류 발생 시 처리
            task_unit_response = TaskUnitResponse.objects.create(
                task_unit=task_unit,
                status=TaskUnitStatus.FAILED,
                request_data=task_unit.text_data,
                error_code="500",  # 예시로 500번 에러 코드
                error_message=str(e),
            )
            calculate_and_save_processing_time(task_unit_response, start_time)
            task_unit.set_status(TaskUnitStatus.FAILED)

            raise self.retry(exc=e, countdown=1)

    except TaskUnit.DoesNotExist as e:
        raise self.retry(exc=e, countdown=1)


@shared_task
def resume_pending_tasks():
    from api.models import TaskUnit, TaskUnitStatus
    pending_or_in_progress_tasks = TaskUnit.objects.filter(
        Q(status=TaskUnitStatus.PENDING) | Q(status=TaskUnitStatus.IN_PROGRESS)
    )
    for task in pending_or_in_progress_tasks:
        process_task_unit.apply_async(args=[task.id])


def calculate_and_save_processing_time(task_unit_response, start_time):
    """작업 시간 계산 후 저장"""
    end_time = time.time()
    processing_time = end_time - start_time

    # 처리 시간 업데이트
    task_unit_response.processing_time = processing_time
