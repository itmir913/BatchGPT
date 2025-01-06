from django.urls import path

from api import views as batch_jobs

urlpatterns = [
    path('<int:task_unit_id>/', batch_jobs.TaskUnits.as_view(), name='task-units-status'),
]
