from django.urls import path, re_path

import web_app.views as views

app_name = 'web_app'

urlpatterns = [
    path('router/', views.home_page_view1, name='home_page'),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('linkage_rules/all/', views.all_linkage_rules_view, name='get-all-linkage-rules'),
    path('linkage_rules/', views.create_or_edit_linkage_rule_view, name='create_new_linkage_rule'),
    path('linkage_rules/delete/<uuid:linkage_rule_uuid>/', views.delete_linkage_rule_view, name='delete_linkage_rule'),
    path('linkage_rules/<uuid:linkage_rule_uuid>/', views.create_or_edit_linkage_rule_view, name='edit_linkage_rule'),
    path('intro/', views.intro, name="intro"),
    re_path(r'.*', views.home_page_view, name='home_page'),

]
