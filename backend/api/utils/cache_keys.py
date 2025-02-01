# cache_keys.py
from typing import Type

from django.core.cache import cache
from django.db import models
from django.shortcuts import get_object_or_404

CACHE_TIMEOUT_BATCH_JOB = 60
CACHE_TIMEOUT_TASK_UNIT = 60
CACHE_TIMEOUT_TASK_UNIT_RESPONSE = 60


def get_cache_or_database(
        model: Type[models.Model],  # Specify the type hint as a subclass of models.Model
        primary_key: int,
        cache_key: str,
        timeout: int
):
    cached = cache.get(cache_key)
    if not cached:
        cached = get_object_or_404(model, id=primary_key)
        cache.set(cache_key, cached, timeout=timeout)
    return cached


def batch_job_cache_key(batch_job_id):
    return f"batch_job:{batch_job_id}"


def task_unit_cache_key(task_unit_id):
    return f"task_unit:{task_unit_id}"


def task_unit_response_cache_key(task_unit_response_id):
    return f"task_unit_response:{task_unit_response_id}"


def user_cache_key(user_id):
    return f"user:{user_id}"


def general_cache_key(model_name, object_id):
    return f"{model_name}:{object_id}"


def batch_job_celery_cache_key(batch_job_id):
    return f"Celery:batch_job:request.id:{batch_job_id}"


def task_unit_celery_cache_key(task_unit_id):
    return f"Celery:task_unit:request.id:{task_unit_id}"


def locked_celery_cache_key(task_type):
    return f"Celery:task:locking:{task_type}"
