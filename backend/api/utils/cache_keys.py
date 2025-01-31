# cache_keys.py

def batch_status_key(batch_id):
    return f"batch_status:{batch_id}"


def task_unit_status_key(task_unit_id):
    return f"task_unit_status:{task_unit_id}"


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
