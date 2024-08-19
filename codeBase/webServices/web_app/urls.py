from django.urls import path

from . import views

app_name = 'web_app'

urlpatterns = [
    path('login/', views.logout_view, name="login"),
    path('linkage_rules/', views.create_or_edit_linkage_rule_view, name='get-all-linkage-rules'),
]