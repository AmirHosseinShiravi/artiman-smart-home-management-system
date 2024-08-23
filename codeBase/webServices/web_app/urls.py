from django.urls import path

import web_app.views as views

app_name = 'web_app'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('linkage_rules/', views.create_or_edit_linkage_rule_view, name='get-all-linkage-rules'),
    path('', views.home_page_view, name='home_page'),
    path('intro/', views.intro, name="intro"),

]
