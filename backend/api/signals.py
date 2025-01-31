from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.models import TaskUnit, BatchJob, TaskUnitResponse
from api.utils.cache_keys import batch_job_cache_key, task_unit_cache_key, task_unit_response_cache_key


def register_signals():
    @receiver(post_save, sender=BatchJob)
    def update_batch_job_cache(sender, instance, **kwargs):
        cache.set(batch_job_cache_key(instance.id), instance, timeout=300)

    @receiver(post_delete, sender=BatchJob)
    def delete_batch_job_cache(sender, instance, **kwargs):
        cache.delete(batch_job_cache_key(instance.id))

    @receiver(post_save, sender=TaskUnit)
    def update_task_unit_cache(sender, instance, **kwargs):
        cache.set(task_unit_cache_key(instance.id), instance, timeout=300)

    @receiver(post_delete, sender=TaskUnit)
    def delete_task_unit_cache(sender, instance, **kwargs):
        cache.delete(task_unit_cache_key(instance.id))

    @receiver(post_save, sender=TaskUnitResponse)
    def update_task_unit_response_cache(sender, instance, **kwargs):
        cache.set(task_unit_response_cache_key(instance.id), instance, timeout=300)

    @receiver(post_delete, sender=TaskUnitResponse)
    def delete_task_unit_response_cache(sender, instance, **kwargs):
        cache.delete(task_unit_response_cache_key(instance.id))
