from django.apps import AppConfig
import sys

class SystemuptimetrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'systemUptimeTracker'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True
        # you must import your modules here 
        # to avoid AppRegistryNotReady exception 
        # from .systemruntimelogger import SystemRuntimeLogger
        # SystemRuntimeLogger.runner()
        # startup code here

