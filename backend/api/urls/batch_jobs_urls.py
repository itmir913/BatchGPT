from django.urls import path

from api import views as batch_jobs

urlpatterns = [
    path('', batch_jobs.UserBatchJobsView.as_view(), name='list-batch-jobs'),
    path('create/', batch_jobs.UserBatchJobsView.as_view(), name='batch-job-create'),
    path('supported-file-types/', batch_jobs.BatchJobSupportFileType.as_view(), name='batch-job-support-type'),

    path('<int:batch_id>/', batch_jobs.BatchJobDetailView.as_view(), name='batch-job-detail'),
    path('<int:batch_id>/upload/', batch_jobs.BatchJobFileUploadView.as_view(), name='batch-job-upload-files'),
    path('<int:batch_id>/configs/', batch_jobs.BatchJobConfigView.as_view(), name='batch-job-configs'),
    path('<int:batch_id>/preview/', batch_jobs.BatchJobPreView.as_view(), name='batch-job-preview'),
    path('<int:batch_id>/task-units/', batch_jobs.TaskUnitResponseListAPIView.as_view(), name='batch-job-task-units'),
    path('<int:batch_id>/task-units/<int:task_unit_id>/', batch_jobs.TaskUnitStatusView.as_view(),
         name='task-units-status'),
    path('<int:batch_id>/run/', batch_jobs.BatchJobRunView.as_view(), name='batch-job-run'),
]
