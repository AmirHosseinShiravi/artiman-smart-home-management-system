from django.urls import path
from .views import create_four_pole_switch, edit_four_pole_switch

urlpatterns = [
    path('device/create/', create_four_pole_switch, name='create_four_pole_switch'),
    path('device/edit/<int:device_id>/', edit_four_pole_switch, name='edit_four_pole_switch'),
]
