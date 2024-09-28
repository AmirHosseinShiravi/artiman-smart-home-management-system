from django.core.management.base import BaseCommand
import core.settings as settings
from systemUptimeTracker.systemRuntimeLogger import SystemRuntimeLogger
from time import sleep


class Command(BaseCommand):
    #TODO: change help note
    help = '''beacause we need one program to log
            system runtime independently from dashboard, this approach is good to run this app seperately.
            
            Command Syntax:
                python manage.py system_runtime_tracker_task
            
            '''
    settings.in_task_mode = True
    def handle(self, *args, **options):
        
        # sleep(5)
        SystemRuntimeLogger.determine_downtime()
        # SystemRuntimeLogger.generate_last_24hrs_runtime_data()
        SystemRuntimeLogger.runner()

        

