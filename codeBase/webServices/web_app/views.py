import json
import uuid
import os
from admin_tabler.forms import LoginForm
from django.contrib.auth.views import LoginView as AuthLoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from dashboard.models import Project, Home, HomeUser, Controller, Zone, DeviceProxy
from .models import LinkageRule
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse, reverse_lazy
from .rule_creator import LinkageRuleCreator
from dashboard.mqtt_manager import subscribe_to_topic
import dotenv

dotenv.load_dotenv()


def intro(request):
    return render(request, 'web_app/pages/intro.html')


class LoginView(AuthLoginView):
    template_name = 'web_app/pages/login.html'
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return reverse('web_app:home_page')

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        response = super().form_valid(form)
        return redirect(self.get_success_url())


def logout_view(request):
    logout(request)
    return redirect("web_app:login")


@login_required(login_url=reverse_lazy("web_app:login"))
def home_page_view(request):
    if not HomeUser.objects.filter(user=request.user).exists():
        return redirect(reverse("web_app:login"))
    user = HomeUser.objects.filter(user=request.user).get()
    home_controllers = Controller.objects.filter(parent_home=user.parent_home, parent_project=user.parent_project).all()
    home_zones = Zone.objects.filter(parent_project=user.parent_project, parent_home=user.parent_home).all()
    home_devices = DeviceProxy.objects.filter(device_base__parent_project=user.parent_project, device_base__parent_home=user.parent_home).all()

    for device in home_devices:
        device_type = device.content_type
        device_object = device.device_base
        device_functions = list(device.device_base.functions.all())
        pass


    emqx_broker_web_app_host = os.environ.get('emqx_broker_web_app_host')
    emqx_broker_web_app_port = int(os.environ.get('emqx_broker_web_app_port'))
    emqx_broker_web_app_ws_path = os.environ.get('emqx_broker_web_app_ws_path')
    emqx_broker_web_app_transport = os.environ.get('emqx_broker_web_app_transport')

    context = {
        "mqtt_broker_host": emqx_broker_web_app_host,
        "mqtt_broker_port": emqx_broker_web_app_port,
        "mqtt_broker_ws_path": emqx_broker_web_app_ws_path,
        "mqtt_broker_transport": emqx_broker_web_app_transport,
        "user": user,
        "home_controllers": [{"controller_name": controller.name,
                              "controller_uuid": str(controller.uuid),
                              "status": controller.status,
                              "enable_internal_server": controller.enable_internal_server,
                              "ip_address": controller.ip_address,
                              "port_number": controller.port_number} for controller in home_controllers],
        "home_zones": [{"zone_name": zone.zone_name, "zone_uuid": str(zone.uuid)} for zone in home_zones]

    }
    # when user authenticate, redirect to this view to load pwa app.
    return render(request, 'web_app/home_page.html', context=context)


def home_page_view1(request):
    # when user authenticate, redirect to this view to load pwa app.
    return render(request, 'experimental/page_router.html')


@login_required(login_url=reverse_lazy("web_app:login"))
def all_linkage_rules_view(request):
    if HomeUser.objects.filter(user=request.user).exists():
        home_user = HomeUser.objects.filter(user=request.user).get()
        linkage_rules = LinkageRule.objects.filter(parent_project=home_user.parent_project, parent_home=home_user.parent_home).all()
        context = {
            "status": "success",
            "linkage_rules": [rule["rule_config"] for rule in linkage_rules.values()]
        }
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse({"status": 404})


@login_required(login_url=reverse_lazy("web_app:login"))
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
            if linkage_rule:
                try:
                    # 1.  create rule engine class
                    # 2. add to database
                    # 3. generate rule uuid and paced in rule config
                    # 4. subscribe to enable/disable rule topic and call a function to set to database

                    rule_config = json.loads(request.body)

                    LinkageRule.objects.filter(id=linkage_rule.id).update(name=rule_config["name"],
                                                                          status=rule_config["status"],
                                                                          rule_config=rule_config,
                                                                          last_edited_by=request.user)

                    created_rule = LinkageRule.objects.get(uuid=rule_config["rule_uuid"])
                    linkage_rule_creator_instance = LinkageRuleCreator(rule_uuid=rule_config["rule_uuid"])
                    linkage_rule_creator_instance.create_linkage_rule_file()
                    setting_home_user_authorization_status = linkage_rule_creator_instance.set_rule_topics_authorization()
                    if not setting_home_user_authorization_status:
                        created_rule.delete()
                        return JsonResponse(
                            {'status': 'error', 'message': 'mqtt server not response.please try later.'}, status=400)

                    linkage_rule_creator_instance.place_linkage_rule_file_to_rule_engine_rules_folder()

                    base_linkage_rule_topics_address = f"v1/projects/{created_rule.parent_project.uuid}/homes/{created_rule.parent_home.uuid}/linkage-rules/{created_rule.uuid}"
                    subscribe_to_topic(base_linkage_rule_topics_address + "/status/get", linkage_rule_status_changer_callback)

                    return JsonResponse({'status': 'success', "rule_uuid": created_rule.uuid})

                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

            else:
                try:
                    # 1. create rule engine class
                    # 2. add to database
                    # 3. generate rule uuid and paced in rule config
                    # 4. subscribe to enable/disable rule topic and call a function to set to database
                    # 5.
                    rule_config = json.loads(request.body)
                    rule_uuid = uuid.uuid4()
                    rule_config["rule_uuid"] = str(rule_uuid)
                    created_rule = LinkageRule.objects.create(name=rule_config["name"],
                                                              uuid=rule_uuid,
                                                              parent_project=home_user.parent_project,
                                                              parent_home=home_user.parent_home,
                                                              rule_config=rule_config,
                                                              created_by=request.user,
                                                              last_edited_by=request.user)

                    linkage_rule_creator_instance = LinkageRuleCreator(rule_uuid=created_rule.uuid)
                    linkage_rule_creator_instance.create_linkage_rule_file()
                    setting_home_user_authorization_status = linkage_rule_creator_instance.set_rule_topics_authorization()
                    if not setting_home_user_authorization_status:
                        created_rule.delete()
                        return JsonResponse({'status': 'error', 'message': 'mqtt server not response.please try later.'}, status=400)

                    linkage_rule_creator_instance.place_linkage_rule_file_to_rule_engine_rules_folder()

                    base_linkage_rule_topics_address = f"v1/projects/{created_rule.parent_project.uuid}/homes/{created_rule.parent_home.uuid}/linkage-rules/{created_rule.uuid}"
                    print(base_linkage_rule_topics_address)
                    subscribe_to_topic(base_linkage_rule_topics_address + "/status/get",
                                       linkage_rule_status_changer_callback)

                    return JsonResponse({'status': 'success', "rule_uuid": created_rule.uuid})

                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)


def linkage_rule_status_changer_callback(topic, payload):
    topic_parts = topic.split("/")
    uuid_index = topic_parts.index("linkage-rules") + 1
    linkage_rule_uuid = topic_parts[uuid_index]
    if LinkageRule.objects.filter(uuid=uuid.UUID(linkage_rule_uuid)).exists():
        desire_rule = LinkageRule.objects.filter(uuid=uuid.UUID(linkage_rule_uuid)).get()
        if payload == "enable":
            desire_rule.status = LinkageRule.RuleStatus.ENABLE
        elif payload == "disable":
            desire_rule.status = LinkageRule.RuleStatus.DISABLE


# @login_required(login_url=reverse_lazy("web_app:login"))
def delete_linkage_rule_view(request, linkage_rule_uuid=None):
    try:
        if linkage_rule_uuid:
            if LinkageRule.objects.filter(uuid=linkage_rule_uuid).exists():
                rule = LinkageRule.objects.filter(uuid=linkage_rule_uuid).get()
                linkage_rule_creator_instance = LinkageRuleCreator(rule_uuid=rule.uuid)
                deletion_status = linkage_rule_creator_instance.delete_linkage_rule_file_from_rule_engine_rules_folder()
                if deletion_status:
                    rule.delete()
                    return JsonResponse({"status": "success", "rule_uuid": linkage_rule_uuid})
                else:
                    return JsonResponse({"status": "error", "rule_uuid": linkage_rule_uuid, "error": "rule file deletion error"})
            else:
                return JsonResponse({"status": "error", "rule_uuid": linkage_rule_uuid, "error": f"Rule not found"},
                                    status=404)

    except Exception as e:
        return JsonResponse({"status": "error", "rule_uuid": linkage_rule_uuid, "error": f"{e}"})