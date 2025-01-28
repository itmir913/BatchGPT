import logging
import os

from celery import shared_task

from api.utils.files_processor.csv_processor import CSVProcessor
from api.utils.files_processor.file_processor import ResultType
from api.utils.files_processor.pdf_processor import PDFProcessor, ProcessMode
from tasks.celery import app

logger = logging.getLogger(__name__)


def handle_request_data(index, batch_job, request_data):
    from api.models import TaskUnit, TaskUnitStatus
    from tasks.queue_task_units import process_task_unit

    if str(request_data).strip():
        task_unit, created = TaskUnit.objects.update_or_create(
            batch_job=batch_job,
            unit_index=index,
            defaults={
                'text_data': request_data,
                'file_data': None,
                'task_unit_status': TaskUnitStatus.PENDING,
                'latest_response': None,
            }
        )
        process_task_unit.apply_async(args=[task_unit.id])


def process_csv(processor, prompt, batch_job, file_path):
    selected_headers = batch_job.configs['selected_headers']
    selected_headers = [header.strip() for header in selected_headers]

    for index, (result_type, data) in enumerate(processor.process(file_path), start=1):
        if result_type == ResultType.TEXT:
            columns, row = data
            request_data = processor.process_text(prompt, columns=columns, row=row, selected_headers=selected_headers)
            handle_request_data(index, batch_job, request_data)
        else:
            raise NotImplementedError


def process_pdf(processor, prompt, batch_job, file_path):
    work_unit = batch_job.configs.get('work_unit', 1)
    pdf_mode = batch_job.configs.get('pdf_mode', ProcessMode.TEXT)

    for index, (result_type, data) in \
            enumerate(processor.process(file_path, work_unit=work_unit, pdf_mode=pdf_mode),
                      start=1):
        if result_type == ResultType.TEXT:
            request_data = processor.process_text(prompt, data=data)
            handle_request_data(index, batch_job, request_data)
        else:
            raise NotImplementedError


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    from django.core.cache import cache
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.shortcuts import get_object_or_404
    from api.models import BatchJob, BatchJobStatus
    from api.utils.file_settings import FileSettings
    from api.utils.cache_keys import batch_status_key
    from backend import settings

    try:
        status = cache.get(batch_status_key(batch_job_id))
        if not status:
            status = BatchJob.objects.get(id=batch_job_id).get_batch_job_status_display()
            cache.set(batch_status_key(batch_job_id), status, timeout=30)
        if status in [BatchJobStatus.COMPLETED_DISPLAY, BatchJobStatus.FAILED_DISPLAY]:
            logger.log(logging.INFO, f"Celery: The job with ID {batch_job_id} has already been completed.")
            return

        batch_job = get_object_or_404(BatchJob, id=batch_job_id)

        try:
            prompt = batch_job.configs.get('prompt', None)

            if prompt is None:
                logger.log(logging.ERROR, f"API: Cannot generate prompts because prompt or selected_headers is None")
                raise ValueError("Cannot generate prompts because prompt or selected_headers is None")

            cache.set(batch_status_key(batch_job_id), BatchJobStatus.IN_PROGRESS_DISPLAY, timeout=30)
            batch_job.set_status(BatchJobStatus.IN_PROGRESS)
            batch_job.save()

            file = batch_job.file
            file_path = file if isinstance(file, InMemoryUploadedFile) else os.path.join(settings.BASE_DIR, file.path)
            processor = FileSettings.get_file_processor(FileSettings.get_file_extension(file_path))
            if processor is None:
                raise ValueError(f"Unsupported file extension for {file_path}")

            if isinstance(processor, CSVProcessor):
                process_csv(processor, prompt, batch_job, file_path)
            elif isinstance(processor, PDFProcessor):
                process_pdf(processor, prompt, batch_job, file_path)
            else:
                raise NotImplementedError("Unsupported processor type")

            logger.log(logging.INFO, f"Celery: All tasks for job with ID {batch_job_id} have been completed.")

        except Exception as e:
            logger.log(logging.INFO,
                       f"Celery: The job with ID {batch_job_id} has failed for the following reason: {str(e)}")
            cache.set(batch_status_key(batch_job_id), BatchJobStatus.FAILED_DISPLAY, timeout=30)
            batch_job.set_status(BatchJobStatus.FAILED)
            batch_job.save()
            return

    except BatchJob.DoesNotExist as e:
        return


@app.task
def resume_pending_jobs():
    from api.models import BatchJob, BatchJobStatus, TaskUnit
    from api.utils.job_status_utils import get_task_status_counts

    pending_or_in_progress_jobs = BatchJob.objects.filter(batch_job_status=BatchJobStatus.PENDING)

    for job in pending_or_in_progress_jobs:
        if TaskUnit.objects.filter(batch_job=job).count() == 0:
            process_batch_job.apply_async(args=[job.id])
        else:
            pending, in_progress, fail = get_task_status_counts(job)

            if pending > 0 or in_progress > 0:
                process_batch_job.apply_async(args=[job.id])
                return
            elif fail > 0:
                job.set_status(BatchJobStatus.FAILED)
                job.save()
            else:
                job.set_status(BatchJobStatus.COMPLETED)
                job.save()
