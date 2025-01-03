from django.urls import path

from . import views  # 앱의 views 모듈 가져오기

urlpatterns = [
    path('login/', views.login, name='login-view'),
    path('register/', views.register_user, name='users-register'),
    path('check/', views.check_authentication, name='check-auth'),
]
