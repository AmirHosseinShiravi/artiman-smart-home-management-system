from django.urls import path, include
from . import views

app_name = 'systemUptimeTracker'

urlpatterns = [
    path("get_system_runtime_data", views.get_system_runtime_data, name="get_system_runtime_data"),
    path("get_system_runtime_data_last_24hrs", views.get_system_runtime_data_last_24hrs, name="get_system_runtime_data_last_24hrs"),
]
