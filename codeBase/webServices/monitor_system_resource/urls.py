from django.urls import path
from .views import get_system_statistics

app_name = 'monitor_system_resource'
urlpatterns = [
    path('system_statistics/', get_system_statistics, name='system_statistics'),
]