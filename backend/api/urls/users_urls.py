from django.urls import path

from users import views  # 앱의 views 모듈 가져오기

urlpatterns = [
    path('<int:user_id>/', views.user_info, name='users-info'),  # GET: user info

    path('<int:user_id>/batch-job/', views.user_batch_job, name='users-batchjob'),  # GET: 전체 목록 조회, POST: 생성

    path('<int:user_id>/batch-job/<int:batchjob_id>/', views.user_batch_job, name='users-batchjob'),
    # GET: 특정 batch-job 조회
]
