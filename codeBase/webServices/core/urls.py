"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import settings
from django.conf.urls.static import static
from web_app import views as web_app_views
urlpatterns = [
    path("dashboard/v1/", include('dashboard.urls', namespace="dashboard")),
    path("web_app/v1/", include('web_app.urls', namespace="web_app")),
    path("system_runtime_tracker/v1/", include('systemUptimeTracker.urls', namespace="systemUptimeTracker")),
    path("monitor_system_resource/v1/", include('monitor_system_resource.urls', namespace="monitor_system_resource")),
    path("admin/", admin.site.urls),
    path('tabler/', include('admin_tabler.urls')),
    path('service-worker.js', web_app_views.serve_service_worker_file, name="service-worker-file"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
