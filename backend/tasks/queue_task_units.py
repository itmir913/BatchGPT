# tasks/queue_task_units.py
import json
import logging
import time

from celery import shared_task
from openai import OpenAI

from api.utils.cache_keys import batch_job_cache_key, \
    CACHE_TIMEOUT_BATCH_JOB, get_cache_or_database
from api.utils.gpt_processor.gpt_settings import get_gpt_processor
from tasks.celery import app

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_task_unit(self, task_unit_id):
    from django.db import connections, transaction
    from api.models import TaskUnit, TaskUnitResponse, TaskUnitStatus, BatchJob, TaskUnitFiles
    from backend.settings import OPENAI_API_KEY

    start_time = time.time()
    task_unit = None
    batch_job = None

    try:
        with transaction.atomic():
            task_unit = TaskUnit.objects.select_for_update(skip_locked=True).filter(id=task_unit_id).first()

            if not task_unit:
                logger.info(f"Celery: The task with ID {task_unit} is already being processed by another worker. "
                            f"Skipping this job.")
                return

            if task_unit.task_unit_status in [TaskUnitStatus.COMPLETED]:
                logger.log(logging.INFO, f"Celery: The task with ID {task_unit_id} has already been completed.")
                return

            task_unit.set_status(TaskUnitStatus.IN_PROGRESS)
            task_unit.save()

        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=task_unit.batch_job_id,
            cache_key=batch_job_cache_key(task_unit.batch_job_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        batch_job_config = batch_job.configs or {}
        model = batch_job_config['gpt_model']

        content_data = [{
            "type": "text",
            "text": task_unit.text_data,
        }]

        if task_unit.has_files:
            task_unit_files = TaskUnitFiles.objects.filter(task_unit=task_unit)
            base64_images = [{
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{task_unit_file.base64_image_data}"},
            } for task_unit_file in task_unit_files]
            content_data += base64_images
            logging.info(logging.INFO,
                         f"Base64 images added to content data. "
                         f"Total content length: {len(content_data)}")

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": content_data,
                }
            ],
            max_tokens=500
        )

        response_json = response.model_dump_json()
        gpt_response = response_json if isinstance(response_json, dict) else json.loads(response_json)
        gpt_processor = get_gpt_processor(company="openai")

        task_unit_response = TaskUnitResponse.objects.create(
            batch_job=batch_job,
            task_unit=task_unit,
            task_unit_index=task_unit.unit_index,
            task_response_status=TaskUnitStatus.COMPLETED,
            request_data=task_unit.text_data,
            response_data=gpt_processor.process_response(gpt_response),
            processing_time=calculate_processing_time(start_time)
        )

        with transaction.atomic():
            task_unit.set_status(TaskUnitStatus.COMPLETED)
            task_unit.latest_response = task_unit_response
            task_unit.save()

        logger.log(logging.INFO, f"Celery: The request for {task_unit_id} has been completed.")

    except Exception as e:
        logger.log(logging.INFO,
                   f"Celery: The request for {task_unit_id} has failed for the following reason: {str(e)}")

        if batch_job and task_unit:
            with transaction.atomic():
                task_unit_response = TaskUnitResponse.objects.create(
                    batch_job=batch_job,
                    task_unit=task_unit,
                    task_unit_index=task_unit.unit_index,
                    task_response_status=TaskUnitStatus.FAILED,
                    request_data=task_unit.text_data,
                    error_message=str(e),
                    processing_time=calculate_processing_time(start_time),
                )

                task_unit.set_status(TaskUnitStatus.FAILED)
                task_unit.latest_response = task_unit_response
                task_unit.save()

        raise self.retry(exc=e, countdown=10)

    finally:
        connections.close_all()


@app.task
def resume_pending_tasks():
    from api.models import TaskUnit, TaskUnitStatus
    from django.db import connections

    try:
        pending_or_in_progress_tasks = TaskUnit.objects.filter(task_unit_status=TaskUnitStatus.PENDING)
        for task in pending_or_in_progress_tasks:
            logger.log(logging.INFO,
                       f"Celery: Pending task {task.id} has been recognized and is now starting.")
            process_task_unit.apply_async(args=[task.id])

    except Exception as e:
        logger.log(logging.INFO,
                   f"Celery: Unknowen Error: {str(e)}")

    finally:
        connections.close_all()


def calculate_processing_time(start_time):
    """작업 시간 계산 후 저장"""
    end_time = time.time()
    return end_time - start_time
