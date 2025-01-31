# cache_keys.py
CACHE_TIMEOUT_BATCH_JOB = 60
CACHE_TIMEOUT_TASK_UNIT = 60
CACHE_TIMEOUT_TASK_UNIT_RESPONSE = 60


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
