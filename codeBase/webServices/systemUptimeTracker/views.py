from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse
from systemUptimeTracker.systemRuntimeLogger import SystemRuntimeLogger
import datetime as dt


@login_required(login_url=reverse_lazy("dashboard:login"))
def get_system_runtime_data(request):
    if request.GET.get('selectedtime'):
        selected_time = dt.datetime.strptime(str(request.GET.get('selectedtime')), '%b %d %Y %H:%M')    
        heatmap_second = SystemRuntimeLogger.generate_periodtime_base_runtime_data(selected_time)
    else:
        selected_time = dt.datetime.now().replace(minute=0, second=0, microsecond=0)
        heatmap_second = SystemRuntimeLogger.generate_periodtime_base_runtime_data(selected_time)
    return JsonResponse({'Data': heatmap_second})


@login_required(login_url=reverse_lazy("dashboard:login"))
def get_system_runtime_data_last_24hrs(request):
    heatmap_hour = SystemRuntimeLogger.generate_last_24hrs_runtime_data()
    return JsonResponse({'Data':heatmap_hour})

