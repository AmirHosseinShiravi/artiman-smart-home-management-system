import psutil
from django.http import JsonResponse
from django.views.generic import TemplateView
from collections import deque
from time import time

# Circular buffers to store usage data
MAX_DATA_POINTS = 1000
cpu_data = deque(maxlen=MAX_DATA_POINTS)
ram_data = deque(maxlen=MAX_DATA_POINTS)
storage_data = deque(maxlen=MAX_DATA_POINTS)


def get_system_statistics(request):
    timestamp = int(time() * 1000)  # Current time in milliseconds
    
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_data.append({'x': timestamp, 'y': cpu_usage})
    
    # Get RAM usage
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    ram_data.append({'x': timestamp, 'y': ram_usage})
    
    # Get storage usage
    storage = psutil.disk_usage('/')
    storage_usage = storage.percent
    storage_data.append({'x': timestamp, 'y': storage_usage})
    
    # Return all data points in the buffers
    return JsonResponse({
        'cpu': list(cpu_data),
        'ram': list(ram_data),
        'storage': list(storage_data)
    })