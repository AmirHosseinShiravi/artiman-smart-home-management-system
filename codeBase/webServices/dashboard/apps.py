from django.apps import AppConfig

from .mqtt_manager_v3 import MQTTAppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    # def ready(self):
    #     initialize_mqtt()
