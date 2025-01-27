# cache_keys.py

def batch_status_key(batch_id):
    return f"batch_status:{batch_id}"


def task_unit_status_key(task_unit_id):
    return f"task_unit_status:{task_unit_id}"
