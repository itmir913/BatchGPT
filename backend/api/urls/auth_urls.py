from django.urls import path

from users import views  # 앱의 views 모듈 가져오기
from users.views import RegisterView

urlpatterns = [
    path('login/', views.login_view, name='auth-login'),
    path('logout/', views.logout_view, name='auth-logout'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('check/', views.check_authentication, name='auth-check'),
]
