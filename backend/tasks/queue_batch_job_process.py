import logging
import os

from celery import shared_task

from api.utils.files_processor.base_processor import ResultType
from api.utils.files_processor.csv_processor import CSVProcessor
from api.utils.files_processor.pdf_processor import PDFProcessor
from tasks.celery import app

logger = logging.getLogger(__name__)


def handle_request_data(index, batch_job, prompt, result_type, files=None):
    from api.models import TaskUnit, TaskUnitStatus, TaskUnitFiles
    from tasks.queue_task_units import process_task_unit

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
                }
            )

            process_task_unit.apply_async(args=[task_unit.id])

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
                }
            )

            TaskUnitFiles.objects.filter(task_unit=task_unit).delete()
            for file in files:
                TaskUnitFiles.objects.create(
                    task_unit=task_unit,
                    base64_image_data=file
                )

            process_task_unit.apply_async(args=[task_unit.id])

        case _:
            raise NotImplementedError


def process_csv(processor, prompt, batch_job, file_path):
    selected_headers = batch_job.configs['selected_headers']
    selected_headers = [header.strip() for header in selected_headers]

    for index, (result_type, data) in enumerate(processor.process(file_path), start=1):

        match result_type:
            case ResultType.TEXT:
                columns, row = data
                request_data = processor.process_text(prompt, columns=columns, row=row,
                                                      selected_headers=selected_headers)
                handle_request_data(index, batch_job, request_data, result_type)

            case _:
                raise NotImplementedError


def process_pdf(processor, prompt, batch_job, file_path):
    work_unit = batch_job.configs.get('work_unit', 1)
    pdf_mode = batch_job.configs.get('pdf_mode')

    for index, (result_type, data) in \
            enumerate(processor.process(file_path, work_unit=work_unit, pdf_mode=pdf_mode),
                      start=1):

        match result_type:
            case ResultType.TEXT:
                request_data = processor.process_text(prompt, data=data)
                handle_request_data(index, batch_job, request_data, result_type)

            case ResultType.IMAGE:
                handle_request_data(index, batch_job, prompt, result_type, files=data)

            case _:
                raise NotImplementedError


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    from django.db import connections, transaction
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from api.models import BatchJob, BatchJobStatus, TaskUnit
    from api.utils.files_processor.file_settings import FileSettings
    from backend import settings

    batch_job = None

    try:
        with transaction.atomic():
            batch_job = BatchJob.objects.select_for_update(skip_locked=True).filter(id=batch_job_id).first()

            if not batch_job:
                return

            if batch_job.batch_job_status in [BatchJobStatus.COMPLETED]:
                return

            TaskUnit.objects.filter(batch_job=batch_job).delete()
            prompt = batch_job.configs.get('prompt', None)
            if not prompt:
                logger.error("Celery: Cannot generate prompts because prompt is None")
                raise ValueError("Cannot generate prompts because prompt is None")

            batch_job.set_status(BatchJobStatus.IN_PROGRESS)
            batch_job.save()

        logger.info(f"Celery: The job with ID {batch_job_id} is being started.")

        file = batch_job.file
        if not file:
            logger.info(f"Celery: The job with ID {batch_job_id} does not have an associated file")
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
        logger.info(f"Celery: The job with ID {batch_job_id} has failed for the following reason: {str(e)}")

        if batch_job:
            with transaction.atomic():
                batch_job.set_status(BatchJobStatus.FAILED)
                batch_job.save()

        raise self.retry(exc=e, countdown=10)

    finally:
        connections.close_all()


@app.task
def resume_pending_jobs():
    from api.models import BatchJob, BatchJobStatus
    from django.db import connections

    try:
        pending_jobs = BatchJob.objects.filter(batch_job_status=BatchJobStatus.PENDING)
        logger.log(logging.INFO, f"Celery: Found {len(pending_jobs)} pending jobs.")

        for job in pending_jobs:
            process_batch_job.apply_async(args=[job.id])

    except Exception as e:
        logger.log(logging.INFO,
                   f"Celery: Unknown Error: {str(e)}")

    finally:
        connections.close_all()
