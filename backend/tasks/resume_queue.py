from celery import shared_task

from .queue_batch_job_process import resume_pending_tasks as batch_job
from .queue_task_units import resume_pending_tasks as task_units


@shared_task
def resume_pending_tasks_task_units():
    task_units.apply_async()


@shared_task
def resume_pending_tasks_batch_job():
    batch_job.apply_async()
