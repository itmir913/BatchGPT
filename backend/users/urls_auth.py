from django.urls import path

from . import views  # 앱의 views 모듈 가져오기
from .views import RegisterView

urlpatterns = [
    path('login/', views.login_view, name='users-login'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('check/', views.check_authentication, name='auth-check'),
]
