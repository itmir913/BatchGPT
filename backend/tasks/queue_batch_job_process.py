import logging
import os

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    # ImportError: cannot import name 'BatchJob' from partially initialized module 'api.models' (most likely due to a circular import)
    from django.core.cache import cache
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.shortcuts import get_object_or_404
    from api.models import BatchJob, BatchJobStatus, TaskUnit, TaskUnitStatus
    from api.utils.file_settings import FileSettings
    from api.utils.cache_keys import batch_status_key
    from backend import settings
    from tasks.queue_task_units import process_task_unit

    try:
        batch_job = get_object_or_404(BatchJob, id=batch_job_id)
        if batch_job.batch_job_status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED]:
            logger.log(logging.INFO, f"Celery: The job with ID {batch_job_id} has already been completed.")
            return

        try:
            file = batch_job.file
            file_path = file if isinstance(file, InMemoryUploadedFile) else os.path.join(settings.BASE_DIR, file.path)

            processor = FileSettings.get_file_processor(FileSettings.get_file_extension(file_path))

            for index, prompt in enumerate(processor.process(batch_job_id, file_path), start=1):
                if str(prompt).strip():
                    task_unit, created = TaskUnit.objects.update_or_create(
                        batch_job=batch_job,
                        unit_index=index,
                        defaults={
                            'text_data': prompt,
                            'file_data': None,
                            'task_unit_status': TaskUnitStatus.PENDING,
                            'latest_response': None,
                        }
                    )
                    process_task_unit.apply_async(args=[task_unit.id])

            cache.set(batch_status_key(batch_job_id), BatchJobStatus.IN_PROGRESS_DISPLAY, timeout=30)
            batch_job.set_status(BatchJobStatus.IN_PROGRESS)
            batch_job.save()

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


@shared_task
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
