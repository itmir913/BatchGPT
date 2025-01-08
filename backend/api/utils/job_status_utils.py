# job_status_utils.py


def get_task_status_counts(batch_job_id):
    from api.models import TaskUnit, TaskUnitStatus

    pending = TaskUnit.objects.filter(batch_job=batch_job_id, task_unit_status=TaskUnitStatus.PENDING).count()
    in_progress = TaskUnit.objects.filter(batch_job=batch_job_id, task_unit_status=TaskUnitStatus.IN_PROGRESS).count()
    fail = TaskUnit.objects.filter(batch_job=batch_job_id, task_unit_status=TaskUnitStatus.FAILED).count()

    return pending, in_progress, fail
