from django.urls import path

from api.views import batch_jobs_views as batch_jobs

urlpatterns = [
    path('', batch_jobs.UserBatchJobsView.as_view(), name='list-batch-jobs'),
    path('create/', batch_jobs.UserBatchJobsView.as_view(), name='batch-job-create'),
    path('<int:id>/', batch_jobs.BatchJobDetailView.as_view(), name='batch-job-detail'),
    path('<int:id>/upload/', batch_jobs.BatchJobFileUploadView.as_view(), name='batch-job-upload-files'),
    path('<int:id>/preview/', batch_jobs.BatchJobPreviewView.as_view(), name='batch-job-preview'),
]
