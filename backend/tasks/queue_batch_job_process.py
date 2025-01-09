import os

from celery import shared_task


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    # ImportError: cannot import name 'BatchJob' from partially initialized module 'api.models' (most likely due to a circular import)
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.db import transaction, IntegrityError
    from django.shortcuts import get_object_or_404
    from api.models import BatchJob, BatchJobStatus, TaskUnit, TaskUnitStatus
    from api.utils.file_settings import FileSettings
    from backend import settings

    try:
        with transaction.atomic():
            batch_job = get_object_or_404(BatchJob, id=batch_job_id)
            if batch_job.batch_job_status in [BatchJobStatus.COMPLETED, BatchJobStatus.FAILED]:
                return

            file = batch_job.file
            if isinstance(file, InMemoryUploadedFile):
                file_path = file  # InMemoryUploadedFile은 경로가 필요 없으므로 그대로 사용
            else:
                file_path = os.path.join(settings.BASE_DIR, file.path)

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
                        }
                    )

            batch_job.set_status(BatchJobStatus.IN_PROGRESS)
            batch_job.save()

    except BatchJob.DoesNotExist as e:
        pass
    except IntegrityError as e:
        pass


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
