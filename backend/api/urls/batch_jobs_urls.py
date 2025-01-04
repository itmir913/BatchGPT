from django.urls import path

from api.views import batch_jobs_views as batch_jobs

urlpatterns = [
    path('', batch_jobs.UserBatchJobsView.as_view(), name='list-batch-jobs'),
    path('create/', batch_jobs.UserBatchJobsView.as_view(), name='batch-job-create'),
]
