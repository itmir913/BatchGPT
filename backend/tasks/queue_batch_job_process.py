import logging
import os

from celery import shared_task
from celery.worker.control import revoke

from api.utils.cache_keys import batch_job_celery_cache_key, locked_celery_cache_key
from api.utils.files_processor.base_processor import ResultType
from api.utils.files_processor.csv_processor import CSVProcessor
from api.utils.files_processor.pdf_processor import PDFProcessor
from tasks.celery import app
from tasks.queue_task_units import process_task_unit

logger = logging.getLogger(__name__)


def handle_request_data(index, batch_job, prompt, result_type, files=None):
    from api.models import TaskUnit, TaskUnitStatus, TaskUnitFiles

    match result_type:
        case ResultType.TEXT:
            if not str(prompt).strip():
                logger.log(logging.ERROR, f"Celery: The request_data cannot be empty or just whitespace.")
                raise ValueError("The request_data cannot be empty or just whitespace.")

            task_unit, created = TaskUnit.objects.update_or_create(
                batch_job=batch_job,
                unit_index=index,
                defaults={
                    'text_data': prompt,
                    'has_files': False,
                    'task_unit_status': TaskUnitStatus.PENDING,
                    'latest_response': None,
                    'is_valid': True,
                }
            )

            return task_unit.id

        case ResultType.IMAGE:
            if files is None:
                logger.log(logging.ERROR, f"Celery: The provided file is None, which is not allowed.")
                raise ValueError("The provided file is None, which is not allowed.")

            task_unit, created = TaskUnit.objects.update_or_create(
                batch_job=batch_job,
                unit_index=index,
                defaults={
                    'text_data': prompt,
                    'has_files': True,
                    'task_unit_status': TaskUnitStatus.PENDING,
                    'latest_response': None,
                    'is_valid': True,
                }
            )

            TaskUnitFiles.objects.filter(task_unit=task_unit).delete()
            for file in files:
                TaskUnitFiles.objects.create(
                    task_unit=task_unit,
                    base64_image_data=file
                )

            return task_unit.id

        case _:
            raise NotImplementedError


def process_csv(processor, prompt, batch_job, file_path):
    selected_headers = batch_job.configs['selected_headers']
    selected_headers = [header.strip() for header in selected_headers]
    task_ids = []

    for index, (result_type, data) in enumerate(processor.process(file_path), start=1):
        match result_type:
            case ResultType.TEXT:
                columns, row = data
                request_data = processor.process_text(prompt, columns=columns, row=row,
                                                      selected_headers=selected_headers)
                task_unit_id = handle_request_data(index, batch_job, request_data, result_type)
                task_ids.append(task_unit_id)

            case _:
                raise NotImplementedError

    for task_id in task_ids:
        process_task_unit.apply_async(args=[task_id])


def process_pdf(processor, prompt, batch_job, file_path):
    work_unit = batch_job.configs.get('work_unit', 1)
    pdf_mode = batch_job.configs.get('pdf_mode')
    task_ids = []

    for index, (result_type, data) in \
            enumerate(processor.process(file_path, work_unit=work_unit, pdf_mode=pdf_mode),
                      start=1):

        match result_type:
            case ResultType.TEXT:
                request_data = processor.process_text(prompt, data=data)
                task_unit_id = handle_request_data(index, batch_job, request_data, result_type)
                task_ids.append(task_unit_id)

            case ResultType.IMAGE:
                task_unit_id = handle_request_data(index, batch_job, prompt, result_type, files=data)
                task_ids.append(task_unit_id)

            case _:
                raise NotImplementedError

    for task_id in task_ids:
        process_task_unit.apply_async(args=[task_id])


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    from django.db import connections, transaction
    from django.core.cache import cache
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from api.models import BatchJob, BatchJobStatus, TaskUnit
    from api.utils.files_processor.file_settings import FileSettings
    from backend import settings

    batch_job = None

    logger.info(f"Celery: The job with ID {batch_job_id} is detected.")

    try:
        cache.set(batch_job_celery_cache_key(batch_job_id), self.request.id, timeout=60 * 5)

        with transaction.atomic():
            batch_job = BatchJob.objects.select_for_update(skip_locked=True).filter(id=batch_job_id).first()

            if not batch_job:
                logger.debug(f"Celery: The job with ID {batch_job_id} is already being processed by another worker. "
                             f"Skipping this job.")
                return

            if batch_job.batch_job_status in [BatchJobStatus.COMPLETED]:
                logger.info(f"Celery: The job with ID {batch_job_id} has already been completed.")
                return

            if batch_job.batch_job_status in [BatchJobStatus.IN_PROGRESS]:
                logger.info(f"Celery: The job with ID {batch_job_id} has already been progressed.")
                return

            prompt = batch_job.configs.get('prompt', None)
            if not prompt:
                logger.error("Celery: Cannot generate prompts because prompt is None")
                raise ValueError("Cannot generate prompts because prompt is None")

            task_units = TaskUnit.objects.filter(batch_job=batch_job)
            if task_units.exists():
                task_units.update(is_valid=False)

                from api.utils.cache_keys import task_unit_celery_cache_key
                from django.core.cache import cache

                for task_unit in task_units:
                    celery_task_id = cache.get(task_unit_celery_cache_key(task_unit.id))
                    revoke(celery_task_id, terminate=True)

            batch_job.set_status(BatchJobStatus.IN_PROGRESS)
            batch_job.save()

        file = batch_job.file
        if not file:
            logger.error(f"Celery: The job with ID {batch_job_id} does not have an associated file")
            return

        file_path = file if isinstance(file, InMemoryUploadedFile) else os.path.join(settings.BASE_DIR, file.path)
        processor = FileSettings.get_file_processor(FileSettings.get_file_extension(file_path))

        if not processor:
            raise ValueError(f"Celery: Unsupported file extension for {file_path}")

        if isinstance(processor, CSVProcessor):
            process_csv(processor, prompt, batch_job, file_path)
        elif isinstance(processor, PDFProcessor):
            process_pdf(processor, prompt, batch_job, file_path)
        else:
            raise NotImplementedError("Celery: Unsupported processor type")

        logger.info(f"Celery: All tasks for job with ID {batch_job_id} have been completed.")

    except Exception as e:
        logger.error(f"Celery: The job with ID {batch_job_id} has failed for the following reason: {str(e)}")

        if batch_job:
            with transaction.atomic():
                batch_job.set_status(BatchJobStatus.FAILED)
                batch_job.save()

        raise self.retry(exc=e, countdown=10)

    finally:
        cache.delete(batch_job_celery_cache_key(batch_job_id))
        connections.close_all()


@app.task
def resume_pending_jobs():
    from api.models import BatchJob, BatchJobStatus
    from django.core.cache import cache
    from django.db import connections

    try:
        if cache.get(locked_celery_cache_key('resume_pending_jobs')): return
        cache.set(locked_celery_cache_key('resume_pending_jobs'), True, timeout=60 * 5)

        pending_job_ids = list(BatchJob.objects.filter(batch_job_status=BatchJobStatus.PENDING)
                               .values_list("id", flat=True))
        logger.log(logging.INFO,
                   f"Celery: Found {len(pending_job_ids)} pending jobs.")

        for job_id in pending_job_ids:
            process_batch_job.apply_async(args=[job_id])

    except Exception as e:
        logger.log(logging.ERROR,
                   f"Celery: Unknown Error: {str(e)}")

    finally:
        cache.delete(locked_celery_cache_key('resume_pending_jobs'))
        connections.close_all()
