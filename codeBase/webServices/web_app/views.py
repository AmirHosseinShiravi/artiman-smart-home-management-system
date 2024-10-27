import json
from pathlib import Path
import uuid
import os
from admin_tabler.forms import LoginForm
from django.contrib.auth.views import LoginView as AuthLoginView
from django.http import FileResponse, HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from dashboard.models import Project, Home, HomeUser, Controller, Zone, DeviceProxy, UIProxy
from .models import LinkageRule
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse, reverse_lazy
from .rule_creator import LinkageRuleCreator
from dashboard.mqtt_manager import subscribe_to_topic, publish_message
import dotenv
from core import settings
import requests
from django.views.decorators.clickjacking import xframe_options_exempt

from django_user_agents.utils import get_user_agent

from .forms import EditProfileBaseUserForm, EditProfileHomeUserForm
from django.template.loader import render_to_string

dotenv.load_dotenv()


def intro(request):
    return render(request, 'web_app/pages/intro.html')


class LoginView(AuthLoginView):
    form_class = LoginForm

    def get_template_names(self):
        user_agent = get_user_agent(self.request)
        if user_agent.is_mobile:
            return ['web_app/pages/login_mobile.html']
        else:
            return ['web_app/pages/sign-in-cover.html']

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

    def dispatch(self, request, *args, **kwargs):
        # Add user_agent to the request object
        request.user_agent = request.META.get('HTTP_USER_AGENT', '')
        return super().dispatch(request, *args, **kwargs)



def logout_view(request):
    logout(request)
    return redirect("web_app:login")


# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from django.http import HttpResponse
# from urllib.parse import urlencode

# def weather_api(request):
#     base_url = "https://www.tomorrow.io/v1/widget"
    
#     # Get all query parameters from the request
#     params = request.GET.dict()
    
#     # Set default values if not provided
#     params.setdefault('language', 'EN')
#     params.setdefault('unitSystem', 'METRIC')
#     params.setdefault('widgetType', 'aqiMini')
#     params.setdefault('skin', 'dark')
#     params.setdefault('locationId', '134698')
    
#     try:
#         # Set up Chrome options for headless browsing
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
        
#         # Create a new Chrome driver instance
#         driver = webdriver.Chrome(options=chrome_options)
        
#         # Construct the full URL with parameters
#         full_url = f"{base_url}?{urlencode(params)}"
        
#         # Navigate to the page
#         driver.get(full_url)
        
#         # Wait for the content to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.TAG_NAME, "body"))
#         )
        
#         # Get the page source
#         html_content = driver.page_source
        
#         # Close the browser
#         driver.quit()
        
#         return HttpResponse(html_content, content_type='text/html')
#     except Exception as e:
#         return HttpResponse(f"Error fetching data: {str(e)}", status=500)





# @xframe_options_exempt
# def proxy_view(request, url):
#     # Your proxy server details
#     proxies = {
#         'http': 'http://localhost:10809',
#         'https': 'https://localhost:10809',
#     }

#     # Forward the request to the target server
#     response = requests.get(url, proxies=proxies)

#     # Create a Django response with the content from the target server
#     django_response = HttpResponse(
#         content=response.content,
#         status=response.status_code,
#         content_type=response.headers['Content-Type']
#     )

#     # Forward relevant headers
#     for header in ['Content-Language', 'Cache-Control']:
#         if header in response.headers:
#             django_response[header] = response.headers[header]

#     return django_response



# edit profile view. this view should serve the edit profile page and handle the form submission for updating the user profile.
@login_required(login_url=reverse_lazy("web_app:login"))
def edit_profile_view(request):
    if request.method == "GET":
        home_user = HomeUser.objects.filter(user=request.user).get()
        edit_profile_base_user_form = EditProfileBaseUserForm(instance=request.user)    
        edit_profile_home_user_form = EditProfileHomeUserForm(instance=home_user)
        
        context = {
            "edit_profile_base_user_form": edit_profile_base_user_form,
            "edit_profile_home_user_form": edit_profile_home_user_form,
            "user": home_user
        }
        user_agent = get_user_agent(request)
        if user_agent.is_tablet:
            rendered_html = render_to_string("web_app/pages/edit-profile.html", context)
        else:
            rendered_html = render_to_string("tablet_webapp/pages/edit-profile.html", context)

        return JsonResponse({"status": "success", "html": rendered_html})
    elif request.method == "POST":

        edit_profile_base_user_form = EditProfileBaseUserForm(request.POST, instance=request.user)
        edit_profile_home_user_form = EditProfileHomeUserForm(request.POST, request.FILES, instance=HomeUser.objects.filter(user=request.user).get())
        if edit_profile_base_user_form.is_valid() and edit_profile_home_user_form.is_valid():
            edit_profile_base_user_form.save()
            edit_profile_home_user_form.save()
            return JsonResponse({"status": "success"})
        else:
            error_message = "Please correct the following errors and try again: "
            if edit_profile_base_user_form.errors:
                error_message += f"{edit_profile_base_user_form.errors}\n"
            if edit_profile_home_user_form.errors:
                error_message += f"{edit_profile_home_user_form.errors}\n"
            return JsonResponse({"status": "error", "message": error_message}, status=400)




@login_required(login_url=reverse_lazy("web_app:login"))
def serve_service_worker_file(request):
    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        file_path = os.path.join(settings.STATICFILES_DIRS[0], Path("webapp/service-worker/service-worker.js"))
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/javascript')
            response['Content-Disposition'] = f'attachment; filename="service-worker.js"'
            response['Content-Type'] = 'text/javascript; charset=utf-8'
            return response
        else:
            return HttpResponseNotFound('<h1>File not found</h1>')
    else:
        file_path = os.path.join(settings.STATICFILES_DIRS[0], Path("tablet_webapp/service-worker/service-worker.js"))
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/javascript')
            response['Content-Disposition'] = f'attachment; filename="service-worker.js"'
            response['Content-Type'] = 'text/javascript; charset=utf-8'
            return response
        else:
            return HttpResponseNotFound('<h1>File not found</h1>')
    



boolean_enum = ["ON", "OFF"]
thermostat_fct_enum = ["Auto", "Manual"]
thermostat_speed_enum = ["Low", "Medium", "High"]
thermostat_operation_mode_enum = ["Heat", "Cool"]
thermostat_temperature_range_enum = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]



@login_required(login_url=reverse_lazy("web_app:login"))
def home_page_view(request):
    if not HomeUser.objects.filter(user=request.user).exists():
        return redirect(reverse("web_app:login"))
    user = HomeUser.objects.filter(user=request.user).get()
    home_controllers = Controller.objects.filter(parent_home=user.parent_home, parent_project=user.parent_project).all()
    home_zones = Zone.objects.filter(parent_project=user.parent_project, parent_home=user.parent_home).exclude(zone_name="Global").all()
    home_devices = DeviceProxy.objects.filter(device_base__parent_project=user.parent_project, device_base__parent_home=user.parent_home).all()
    all_devices = []
    for device in home_devices:
        device_type = device.content_type # .name and .model
        device_object = device.device_base # name parent_controller parent home parent project parent zone  uuid
        device_functions = list(device.device_base.functions.all()) # display name functiion_name value_type
        device_data_points = []
        for data_point in device_functions:
            type_enum = []
            if data_point.value_type == "BOOLEAN":
                type_enum = boolean_enum
            elif data_point.value_type == "STRING":
                if data_point.thermostatdatapointfunction:
                    if data_point.function_name == "fms":
                        type_enum = thermostat_speed_enum
                    elif data_point.function_name == "fct":
                        type_enum = thermostat_fct_enum
                    elif data_point.function_name == "hc":
                        type_enum = thermostat_operation_mode_enum

            elif data_point.value_type == "DECIMAL":
                type_enum = thermostat_temperature_range_enum

            device_data_points.append({
                "display_name": data_point.display_name,
                "function_name": data_point.function_name,
                "type": data_point.value_type,
                "typeEnum": type_enum,
                "io_permission": data_point.io_permission
            })
        all_devices.append({
            "device_uuid": device_object.uuid,
            "zone_uuid": device_object.parent_zone.uuid,
            "controller_uuid": device_object.parent_controller.uuid,
            "name": device_object.name,
            "device_type": device_type.model,
            "dataPointFunctions": device_data_points
        })


    all_home_ui_elements = UIProxy.objects.filter(ui_base__parent_home=user.parent_home, ui_base__parent_project=user.parent_project).all()
    all_home_ui_elements_dict = []
    for ui_element in all_home_ui_elements:
        ui_base = ui_element.ui_base
        specific_ui = ui_element.content_object
        ui_type = ui_element.content_type.model

        ui_data = {
            "uuid": str(ui_base.uuid),
            "name": ui_base.name,
            "descriptions": ui_base.descriptions,
            "button_name": ui_base.button_name,
            "on_text": ui_base.on_text,
            "off_text": ui_base.off_text,
            "on_color": ui_base.on_color,
            "off_color": ui_base.off_color,
            "on_icon": ui_base.on_icon,
            "off_icon": ui_base.off_icon,
            "add_to_home": ui_base.add_to_home,
            "background_image": ui_base.tablet_mode_background_image.background_image.url,
            "background_image_style": ui_base.tablet_mode_background_image.style_options,
            "button_type": specific_ui.button_type,
            "zone_uuid": str(ui_base.parent_zone.uuid),
            "ui_type": ui_type,
            "datapoint_functions": []
        }

        if ui_type == 'switchui':
            dpf = specific_ui.data_point_function
            ui_data["datapoint_functions"].append({
                "display_name": dpf.display_name,
                "function_name": dpf.function_name,
                "value_type": dpf.value_type,
                "device_uuid": str(dpf.device_base.uuid)
            })
        elif ui_type == 'pushbuttonui':
            dpf = specific_ui.data_point_function
            ui_data["datapoint_functions"].append({
                "display_name": dpf.display_name,
                "function_name": dpf.function_name,
                "value_type": dpf.value_type,
                "device_uuid": str(dpf.device_base.uuid)
            })
        elif ui_type == 'curtainui':
            ui_data["animation_duration"] = specific_ui.animation_duration
            for dpf in [specific_ui.open_data_point_function, specific_ui.close_data_point_function]:
                if dpf == specific_ui.open_data_point_function:
                    ui_data["datapoint_functions"].append({
                        "curtain_function": "open",
                        "display_name": dpf.display_name,
                        "function_name": dpf.function_name,
                        "value_type": dpf.value_type,
                            "device_uuid": str(dpf.device_base.uuid)
                        })
                elif dpf == specific_ui.close_data_point_function:
                    ui_data["datapoint_functions"].append({
                        "curtain_function": "close",
                        "display_name": dpf.display_name,
                        "function_name": dpf.function_name,
                        "value_type": dpf.value_type,
                        "device_uuid": str(dpf.device_base.uuid)
                    })
        elif ui_type == 'thermostatui':
            for dpf in [specific_ui.power_status_function, specific_ui.current_temp_function, 
                        specific_ui.target_temp_function, specific_ui.speed_function, 
                        specific_ui.control_mode_function, specific_ui.operation_mode_function]:
                ui_data["datapoint_functions"].append({
                    "display_name": dpf.display_name,
                    "function_name": dpf.function_name,
                    "value_type": dpf.value_type,
                    "device_uuid": str(dpf.device_base.uuid)
                })

        all_home_ui_elements_dict.append(ui_data)


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
        "home_zones": [{"zone_name": zone.zone_name, "zone_uuid": str(zone.uuid)} for zone in home_zones],
        "all_devices": all_devices,
        "all_home_ui_elements": all_home_ui_elements_dict
    }

    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(request, 'web_app/home_page.html', context=context)
    else:
        return render(request, 'tablet_webapp/home_page.html', context=context)
    # when user authenticate, redirect to this view to load pwa app.
    # return render(request, 'web_app/home_page.html', context=context)


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
                        # created_rule.delete()
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
                    # if rule exist in database, reject it

                    # if LinkageRule.objects.filter(name=rule_config["name"], parent_project=home_user.parent_project, parent_home=home_user.parent_home).exists() or \
                    #    LinkageRule.objects.filter(rule_config__name=rule_config["name"], parent_project=home_user.parent_project, parent_home=home_user.parent_home).exists() or \
                    #    LinkageRule.objects.filter(rule_config__index=rule_config["index"], parent_project=home_user.parent_project, parent_home=home_user.parent_home).exists():
                    #     return JsonResponse({'status': 'error', 'message': 'Rule already exists'}, status=400)
                    
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
    else:
        return JsonResponse({"status": 404})

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
                    parent_project = rule.parent_project
                    parent_home = rule.parent_home
                    rule.delete()
                    rules = LinkageRule.objects.filter(parent_project=parent_project, parent_home=parent_home).all()
                    if rules:
                        # two process, one for automation rules and one for scenes
                        scene_rules_counter = 0
                        automation_rules_counter = 0
                        for rule in rules:
                            if rule.rule_config["type"] == "scene":
                                rule.rule_config["index"] = scene_rules_counter
                                scene_rules_counter += 1
                                rule.save()
                            elif rule.rule_config["type"] == "automation":
                                rule.rule_config["index"] = automation_rules_counter
                                automation_rules_counter += 1
                                rule.save()
                    return JsonResponse({"status": "success", "rule_uuid": linkage_rule_uuid})
                else:
                    return JsonResponse({"status": "error", "rule_uuid": linkage_rule_uuid, "error": "rule file deletion error"})
            else:
                return JsonResponse({"status": "error", "rule_uuid": linkage_rule_uuid, "error": f"Rule not found"},
                                    status=404)

    except Exception as e:
        return JsonResponse({"status": "error", "rule_uuid": linkage_rule_uuid, "error": f"{e}"})
    



# an mqtt listener that get all topics that have /get in the end and redirect it's messages to correspond topics that have /set in the end
def mqtt_listener_for_get_and_set(topic, payload):
    if topic.endswith("/set"):
        correspond_topic = topic.replace("/set", "/get")
        publish_message(correspond_topic, payload, retain=True, qos=1)

# if not settings.in_task_mode:
#     subscribe_to_topic("#", mqtt_listener_for_get_and_set)
