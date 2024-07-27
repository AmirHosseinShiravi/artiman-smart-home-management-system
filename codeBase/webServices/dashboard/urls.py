from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('amir/', views.amir, name='amir'),
    path('settings/', views.settings, name='settings'),
    path('settings_button1/', views.settings_button, name='settings_button1'),

]