from django.http import JsonResponse
from django.shortcuts import render
from dashboard.models import Project, Home, HomeUser
from .models import LinkageRule
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse


def login_view(request):
    pass


def logout_view(request):
    logout(request)


def home_page_view(request):
    # when user authenticate, redirect to this view an load pwa app.
    pass

@login_required(login_url=reverse("web_app:login"))
def all_linkage_rules_view(request):
    if HomeUser.objects.filter(user=request.user).exists():
        home_user = HomeUser.objects.filter(user=request.user).get()
        linkage_rules = LinkageRule.objects.filter(parent_project=home_user.parent_project, parent_home=home_user.parent_home).all()
        context = {
            "status": "success",
            "linkage_rules": linkage_rules
        }
        return JsonResponse(context)
    else:
        return JsonResponse({"status": 404})

@login_required(login_url=reverse("web_app:login"))
def create_or_edit_linkage_rule_view(request, linkage_rule_uuid=None):
    if HomeUser.objects.filter(user=request.user).exists():
        home_user = HomeUser.objects.filter(user=request.user).get()
        if linkage_rule_uuid:
            linkage_rule = LinkageRule.objects.filter(uuid=linkage_rule_uuid,
                                                       parent_project=home_user.parent_project,
                                                       parent_home=home_user.parent_home).get()
        else:
            linkage_rule = None

        if request.method == "GET":
            pass
        if request.method == "POST":
            pass



@login_required(login_url=reverse("web_app:login"))
def delete_linkage_rule_view(request):
    pass
