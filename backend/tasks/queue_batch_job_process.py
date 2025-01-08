from celery import shared_task
from django.db.models import Q


@shared_task(bind=True, max_retries=1, autoretry_for=(Exception,))
def process_batch_job(self, batch_job_id):
    # ImportError: cannot import name 'BatchJob' from partially initialized module 'api.models' (most likely due to a circular import)
    from api.models import BatchJob, BatchJobStatus

    try:
        batch_job = BatchJob.objects.get(id=batch_job_id)
        if batch_job.batch_job_status == BatchJobStatus.COMPLETED:
            return

        # 나누기 작업 이 부분에서 해야 함

        # TODO 하나씩 가져와서 만들기

        batch_job_config = batch_job.configs or {}
        model = batch_job_config['gpt_model']

        # TODO 이제 끝.
        batch_job.set_status(BatchJobStatus.IN_PROGRESS)
        batch_job.save()

    except BatchJob.DoesNotExist as e:
        pass


@shared_task
def resume_pending_tasks():
    from api.models import BatchJob, BatchJobStatus
    pending_or_in_progress_tasks = BatchJob.objects.filter(
        Q(task_unit_status=BatchJobStatus.PENDING) | Q(task_unit_status=BatchJobStatus.IN_PROGRESS)
    )
    for task in pending_or_in_progress_tasks:
        process_task_unit.apply_async(args=[task.id])
