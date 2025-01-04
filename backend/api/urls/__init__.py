# urls/__init__.py
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('auth/', include('api.urls.auth_urls')),
    path('users/', include('api.urls.users_urls')),

]
