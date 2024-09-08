from django.urls import path

from . import views

from admin_tabler.views import LoginView as adminTablerLoginView
app_name = 'dashboard'

urlpatterns = [
    path('accounts/login/', adminTablerLoginView.as_view(), name='login'),
    path('amir/', views.amir, name='amir'),
    path('settings/', views.settings, name='settings'),
    path('settings_button1/', views.settings_button, name='settings_button1'),

    path('projects/all/', views.all_projects_view, name='projects_view'),
    path('projects/new_project/', views.create_or_edit_project, name='create_new_project'),
    path('projects/edit/<uuid:project_uuid>/', views.create_or_edit_project, name='edit_project'),
    path('projects/delete/<uuid:project_uuid>/', views.delete_project, name='delete_project'),
    # project Homes section
    path('projects/<uuid:project_uuid>/homes/all/', views.project_all_homes_view, name='project_all_homes'),

    path('projects/<uuid:project_uuid>/homes/new_home/', views.create_or_edit_home, name='create_new_home'),
    path('projects/<uuid:project_uuid>/homes/edit/<uuid:home_uuid>/', views.create_or_edit_home, name='edit_home'),
    path('projects/<uuid:project_uuid>/homes/delete/<uuid:home_uuid>/', views.delete_home, name='delete_home'),

    # home settings dedicated page
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/', views.view_selected_home_settings_page, name='home_wizards'),


    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/overview/', views.home_overview_view, name='home_overview'),

    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/settings/', views.home_general_settings_section_view, name='home_wizard_home_settings'),



    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/tablet/', views.home_tablet_section_view, name='home_wizard_tablet_settings'),



    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/users/', views.home_all_users_view, name='home_wizard_all_users'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/users/create_new_user/', views.create_or_edit_home_user_view, name='home_wizard_create_new_user'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/users/edit/<uuid:user_uuid>/', views.create_or_edit_home_user_view, name='home_wizard_edit_user'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/users/delete/<uuid:user_uuid>/', views.delete_home_user_view, name='home_wizard_delete_user'),

    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/zones/', views.home_all_zones_view, name='home_wizard_all_zones'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/zones/create_new_zone/', views.create_or_edit_home_zone_view, name='home_wizard_create_new_zone'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/zones/edit/<uuid:zone_uuid>/', views.create_or_edit_home_zone_view, name='home_wizard_edit_zone'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/zones/delete/<uuid:zone_uuid>/', views.delete_home_zone_view, name='home_wizard_delete_zone'),

    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/controllers/', views.home_all_controller_view, name='home_wizard_all_controllers'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/controllers/create_new_controller/', views.create_or_edit_home_controller_view, name='home_wizard_create_new_controller'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/controllers/edit/<uuid:controller_uuid>/', views.create_or_edit_home_controller_view, name='home_wizard_edit_controller'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/controllers/delete/<uuid:controller_uuid>/', views.delete_home_controller_view, name='home_wizard_delete_controller'),

    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/controllers/get_config/<uuid:controller_uuid>/',views.download_home_controller_config_view, name='home_wizard_download_controller_config'),


    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/devices/', views.home_all_devices_view, name='home_wizard_all_devices'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/devices/create_new_device/', views.create_or_edit_home_device_view, name='home_wizard_create_new_device'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/devices/edit/<uuid:device_uuid>/', views.create_or_edit_home_device_view, name='home_wizard_edit_device'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/devices/delete/<uuid:device_uuid>/', views.delete_home_device_view, name='home_wizard_delete_device'),



    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/ui/', views.home_all_ui_elements_view, name='home_wizard_all_ui_elements'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/ui/create_new_ui/', views.create_or_edit_home_ui_element_view, name='home_wizard_create_new_ui_element'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/ui/edit/<uuid:ui_element_uuid>/', views.create_or_edit_home_ui_element_view, name='home_wizard_edit_ui_element'),
    path('projects/<uuid:project_uuid>/homes/<uuid:home_uuid>/wizard/ui/delete/<uuid:ui_element_uuid>/', views.delete_home_ui_element_view, name='home_wizard_delete_ui_element'),



    path('actionForm/', views.manage_device_switch_actions, name='actionnnnn'),
    path('font/', views.font, name='actionnnnn'),
    path('actionForm2/', views.manage_device_actions, name='action2'),

    path('create_user/', views.create_user, name='create_user1'),


]












