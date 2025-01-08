import os

from celery import shared_task
from django.db.models import Q

from api.utils.file_settings import FileSettings


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    # ImportError: cannot import name 'BatchJob' from partially initialized module 'api.models' (most likely due to a circular import)
    from api.models import BatchJob, BatchJobStatus, TaskUnit, TaskUnitStatus
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from backend import settings

    try:
        batch_job = BatchJob.objects.get(id=batch_job_id)
        if batch_job.batch_job_status == BatchJobStatus.COMPLETED:
            return

        file = batch_job.file
        if isinstance(file, InMemoryUploadedFile):
            file_path = file  # InMemoryUploadedFile은 경로가 필요 없으므로 그대로 사용
        else:
            file_path = os.path.join(settings.BASE_DIR, file.path)

        processor = FileSettings.get_file_processor(FileSettings.get_file_extension(file_path))

        for index, prompt in enumerate(processor.process(batch_job_id, file_path), start=1):
            if prompt is not None:
                task_unit = TaskUnit(
                    batch_job=batch_job,
                    unit_index=index,
                    text_data=prompt,
                    file_data=None,
                    task_unit_status=TaskUnitStatus.PENDING,
                )
                task_unit.save()

        batch_job.set_status(BatchJobStatus.IN_PROGRESS)
        batch_job.save()

    except BatchJob.DoesNotExist as e:
        pass


@shared_task
def resume_pending_tasks():
    from api.models import BatchJob, BatchJobStatus
    pending_or_in_progress_tasks = BatchJob.objects.filter(
        Q(batch_job_status=BatchJobStatus.PENDING) | Q(batch_job_status=BatchJobStatus.IN_PROGRESS)
    )
    for task in pending_or_in_progress_tasks:
        process_batch_job.apply_async(args=[task.id])
