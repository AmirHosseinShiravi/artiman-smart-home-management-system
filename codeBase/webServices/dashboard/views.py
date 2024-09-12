import json
import time
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from .mqtt_manager import initialize_mqtt, subscribe_to_topic, publish_message

from .utils import (generate_random_username,
                    generate_random_password,
                    generate_controller_credentials,
                    add_user_to_emqx_password_based_built_in_database_authentication_backend,
                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend,
                    set_web_app_client_rule_to_emqx_built_in_database_authorization_backend,
                    set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend,
                    delete_all_controller_client_authorization_rules,
                    delete_all_web_app_client_authorization_rules,
                    delete_all_tablet_client_authorization_rules,
                    delete_user_from_emqx_password_based_built_in_database_authentication_backend)

from .models import (Project,
                     Home,
                     Tablet,
                     HomeUser,
                     Zone,
                     Controller,
                     DeviceBase,
                     DeviceProxy,
                     DeviceSwitchActions,
                     FourPoleSwitch,
                     FivePoleSwitch,
                     FourPoleThermostat,
                     TenPoleThermostat,
                     DataPointFunction,
                     UIBase,
                     UIProxy,
                     SwitchUI,
                     PushButtonUI,
                     ThermostatUI,
                     CurtainUI)

from .forms import (ProjectForm,
                    HomeForm,
                    TabletForm,
                    UserForm,
                    HomeUserForm,
                    ZoneForm,
                    ControllerForm,
                    ControllerCredentialForm,
                    FourPoleSwitchForm,
                    FivePoleSwitchForm,
                    FourPoleThermostatForm,
                    TenPoleThermostatForm,
                    UIBaseForm,
                    SwitchUIForm,
                    PushButtonUIForm,
                    CurtainUIForm,
                    ThermostatUIForm,
                    fourPoleSwitch_dataPointFunction_formSet,
                    fivePoleSwitch_dataPointFunction_formSet,
                    thermostat_dataPointFunction_formSet,
                    thermostat_of_fourPoleThermostat_dataPointFunction_formSet,
                    switches_of_tenPoleThermostat_dataPointFunction_formSet,
                    thermostat_of_tenPoleThermostat_dataPointFunction_formSet,
                    four_pole_switch_data_point_function_formset_initial,
                    five_pole_switch_data_point_function_formset_initial,
                    switches_of_ten_pole_thermostat_data_point_function_formset_initial,
                    thermostat_data_point_formset_initial)

from django.contrib.auth.views import LoginView as dashboardLogin
from admin_tabler.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout


class LoginView(dashboardLogin):
    template_name = 'pages/sign-in.html'
    form_class = LoginForm


def logout_view(request):
    logout(request)
    return redirect('dashboard:login')


############## Projects Section ###############

def all_projects_view(request):
    projects = Project.objects.all()

    context = {
        "segment": "projects",
        "projects": projects
    }
    return render(request, "dashboard/projects.html", context=context)


def create_or_edit_project(request, project_uuid=None):
    if project_uuid:
        # Edit existing project
        project = get_object_or_404(Project, uuid=project_uuid)
    else:
        # Create new project
        project = None

    if request.method == "GET":
        if project:
            form = ProjectForm(instance=project)
            return render(request, 'dashboard/project_settings.html',
                          context={'forms': form, 'project_uuid': project_uuid, 'form_type': 'edit_project'})
        else:
            form = ProjectForm()
            return render(request, 'dashboard/project_settings.html',
                          context={'forms': form, 'form_type': 'create_new_project'})

    if request.method == "POST":
        if project:
            form = ProjectForm(request.POST, request.FILES, instance=project)
        else:
            form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            project_instance = form.save(commit=False)
            if not project:
                project_instance.created_by = request.user  # Set the creator field for new projects
                project_instance.last_edited_by = request.user  # Set the creator field for new projects

            if project:
                project_instance.last_edited_by = request.user  # Set the creator field for new projects

            project_instance.save()
            return redirect("dashboard:projects_view")

        return JsonResponse({'response': form.errors})


def delete_project(request, project_uuid=None):
    if project_uuid:
        # Edit existing project
        project = get_object_or_404(Project, uuid=project_uuid)
    else:
        # Create new project
        project = None

    if project:
        Project.objects.get(id=project.id).delete()
        return redirect('dashboard:projects_view')
    else:
        return redirect('dashboard:projects_view')


############### Project Homes Section ###############

def project_all_homes_view(request, project_uuid):
    homes = Home.objects.filter(parent_project__uuid=project_uuid).all()
    project = Project.objects.get(uuid=project_uuid)
    context = {
        "homes": homes,
        "project": project
    }
    return render(request, "dashboard/project_homes.html", context=context)


def create_or_edit_home(request, project_uuid=None, home_uuid=None):
    if home_uuid:
        # Edit existing project
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)

    else:
        # Create new home
        home = None

    if request.method == "GET":
        if home:
            form = HomeForm(instance=home)
            return render(request, 'dashboard/home_settings.html',
                          context={'forms': form, 'project_uuid': project_uuid, 'home_uuid': home_uuid,
                                   'form_type': 'edit_home'})
        else:
            form = HomeForm()
            return render(request, 'dashboard/home_settings.html',
                          context={'forms': form, 'form_type': 'create_new_home', 'project_uuid': project_uuid})

    if request.method == "POST":
        if home:
            form = HomeForm(request.POST, request.FILES, instance=home)
        else:
            form = HomeForm(request.POST, request.FILES)

        if form.is_valid():
            home_instance = form.save(commit=False)
            if not home:
                home_instance.created_by = request.user  # Set the creator field for new homes
                home_instance.last_edited_by = request.user  # Set the creator field for new homes
                home_instance.parent_project = Project.objects.get(uuid=project_uuid)

            if home:
                home_instance.last_edited_by = request.user  # Set the creator field for new homes

            home_instance.save()
            return redirect("dashboard:project_all_homes", project_uuid=project_uuid)

        return JsonResponse({'response': form.errors})


def delete_home(request, project_uuid=None, home_uuid=None):
    if project_uuid and home_uuid:
        # Edit existing project
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
    else:
        # Create new project
        home = None

    if home:
        Home.objects.get(id=home.id).delete()
        return redirect('dashboard:project_all_homes', project_uuid)
    else:
        return redirect('dashboard:project_all_homes', project_uuid)


############### Home Section ##################

def home_overview_view(request, project_uuid=None, home_uuid=None):
    home = Home.objects.get(uuid=home_uuid, parent_project__uuid=project_uuid)
    project = Project.objects.get(uuid=project_uuid)
    zones = Zone.objects.filter(parent_project__uuid=project_uuid, parent_home__uuid=home_uuid).all()

    context = {
        "home": home,
        "project": project,
        "zones": zones,
    }
    return render(request, "dashboard/home_wizard/home_overview.html", context=context)


def view_selected_home_settings_page(request, project_uuid, home_uuid):
    # show page loader when switch between menu links.
    context = {
        'project': Project.objects.get(uuid=project_uuid),
        'home': Home.objects.get(uuid=home_uuid),
        'segment': 'settings'
    }
    # show home settings as default temporary. replace by overview page at the future.
    # return render(request, 'dashboard/home_wizard.html', context=context)
    # return render(request, 'dashboard/home_wizard/settings.html', context=context)
    return redirect('dashboard:home_wizard_home_settings', project_uuid, home_uuid)


def home_general_settings_section_view(request, project_uuid=None, home_uuid=None):
    message = request.GET.get('message', None)
    if home_uuid and project_uuid:
        # Edit existing project
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)

    else:
        # Create new home
        home = None
        project = None
    if request.method == "GET":
        if home and project:
            form = HomeForm(instance=home)

            context = {
                'parent': 'home_settings',
                'segment': 'settings',
                'forms': form,
                'project': project,
                'home': home,
            }
            if message:
                context['message'] = message

            return render(request, 'dashboard/home_wizard/settings.html', context)

    if request.method == "POST":
        if home and project:
            form = HomeForm(request.POST, request.FILES, instance=home)
            if form.is_valid():
                home_instance = form.save(commit=False)
                if not home:
                    home_instance.created_by = request.user  # Set the creator field for new homes
                    home_instance.last_edited_by = request.user  # Set the creator field for new homes
                    home_instance.parent_project = Project.objects.get(uuid=project_uuid)

                if home:
                    home_instance.last_edited_by = request.user  # Set the creator field for new homes
                home_instance.save()

                return redirect(
                    f"{reverse('dashboard:home_wizard_home_settings', args=[project_uuid, home_uuid])}?message=successfully changed")
            return JsonResponse({'response': form.errors})

        else:
            return JsonResponse({'response': "home not found."})


def home_tablet_section_view(request, project_uuid=None, home_uuid=None):
    message = request.GET.get('message', None)
    if home_uuid and project_uuid:
        # Edit existing project
        if Tablet.objects.filter(parent_home__uuid=home_uuid, parent_project__uuid=project_uuid).exists():
            tablet = Tablet.objects.get(parent_home__uuid=home_uuid, parent_project__uuid=project_uuid)
        else:
            tablet = None

        home = get_object_or_404(Home, uuid=home_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)

    else:
        # Create new home
        tablet = None
        home = get_object_or_404(Home, uuid=home_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)

    if request.method == "GET":
        if tablet and home and project:
            form = TabletForm(instance=tablet)

            context = {
                'segment': 'tablet',
                'forms': form,
                'project': project,
                'home': home,
                'tablet': tablet,
            }
            if message:
                context['message'] = message

            return render(request, 'dashboard/home_wizard/tablet.html', context)
        else:
            form = TabletForm()

            context = {
                'segment': 'tablet',
                'forms': form,
                'project': project,
                'home': home
            }
            if message:
                context['message'] = message

            return render(request, 'dashboard/home_wizard/tablet.html', context)

    if request.method == "POST":
        if tablet and home and project:
            form = TabletForm(request.POST, request.FILES, instance=tablet)
        else:
            form = TabletForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data.get('status', None):
                tablet_instance = form.save(commit=False)
                if not tablet:
                    # tablet_instance.created_by = request.user  # Set the creator field for new homes
                    # tablet_instance.last_edited_by = request.user  # Set the creator field for new homes
                    tablet_instance.parent_project = Project.objects.get(uuid=project_uuid)
                    tablet_instance.parent_home = Home.objects.get(uuid=home_uuid)

                # if tablet:
                #     # tablet_instance.last_edited_by = request.user  # Set the creator field for new homes

                tablet_instance.save()

                # add tablet user to HomeUser table
                # TODO[-]: If we haven't at least one Tablet HomeUser, we create one by below code.
                #       but if we create a tablet homeUser account and in all home users section and editing this user
                #       and disable it's is_tablet_user flag, then come to tablet section and enabling tablet_status,
                #       this action make a new tablet account and it maybe not our desire.

                if not HomeUser.objects.filter(parent_home__uuid=home_uuid, parent_project__uuid=project_uuid,
                                               is_tablet_user=True).exists():
                    tablet_user = User.objects.create_user(username=generate_random_username(length=12),
                                                           password=generate_random_password(length=12))
                    if hasattr(tablet_user, 'homeUser'):
                        tablet_home_user = tablet_user.homeUser
                        tablet_home_user.parent_home = home
                        tablet_home_user.parent_project = project
                        tablet_home_user.is_tablet_user = True
                        tablet_home_user.last_edited_by = request.user
                        tablet_user.homeUser.save()
                    else:
                        HomeUser.objects.create(user=tablet_user, parent_home=home, parent_project=project,
                                                is_tablet_user=True,
                                                created_by=request.user, last_edited_by=request.user)
            else:
                tablet_instance = form.save(commit=False)
                if not tablet:
                    tablet_instance.parent_project = Project.objects.get(uuid=project_uuid)
                    tablet_instance.parent_home = Home.objects.get(uuid=home_uuid)
                tablet_instance.save()

                # delete created tablet user
                # log out tablet user(expire jwt tokens)

            return redirect(
                f"{reverse('dashboard:home_wizard_tablet_settings', args=[project_uuid, home_uuid])}?message=successfully changed")

        else:
            return JsonResponse({'response': form.errors})


def home_all_zones_view(request, project_uuid=None, home_uuid=None):
    home = Home.objects.get(uuid=home_uuid, parent_project__uuid=project_uuid)
    project = Project.objects.get(uuid=project_uuid)
    zones = Zone.objects.filter(parent_project__uuid=project_uuid, parent_home__uuid=home_uuid).all()
    zone_form = ZoneForm()
    context = {
        'segment': 'zones',
        "home": home,
        "project": project,
        "zones": zones,
        'zone_form': zone_form
    }
    return render(request, "dashboard/home_wizard/all_zones.html", context=context)


def create_or_edit_home_zone_view(request, project_uuid=None, home_uuid=None, zone_uuid=None):
    if zone_uuid and project_uuid and home_uuid:
        # Edit existing project
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        zone = get_object_or_404(Zone, uuid=zone_uuid, parent_project__uuid=project_uuid, parent_home__uuid=home_uuid)

    else:
        # Create new home
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        zone = None

    if request.method == "GET":
        pass
    if request.method == "POST":
        if zone:
            zone_form = ZoneForm(request.POST, request.FILES, instance=zone)
        else:
            zone_form = ZoneForm(request.POST, request.FILES)

        if zone_form.is_valid():
            zone_instance = zone_form.save(commit=False)

            if not zone:
                zone_instance.parent_project = project
                zone_instance.parent_home = home
                zone_instance.created_by = request.user
                zone_instance.last_edited_by = request.user
            else:
                zone_instance.last_edited_by = request.user
            zone_instance.save()

        return redirect('dashboard:home_wizard_all_zones', project_uuid=project.uuid, home_uuid=home.uuid)


def delete_home_zone_view(request, project_uuid=None, home_uuid=None, zone_uuid=None):
    if zone_uuid and project_uuid and home_uuid:
        # Edit existing project
        zone = get_object_or_404(Zone, uuid=zone_uuid, parent_project__uuid=project_uuid, parent_home__uuid=home_uuid)
    else:
        # Create new project
        zone = None

    if zone:
        Zone.objects.get(id=zone.id).delete()
        return redirect('dashboard:home_wizard_all_zones', project_uuid, home_uuid)
    else:
        return redirect('dashboard:home_wizard_all_zones', project_uuid, home_uuid)


def home_all_users_view(request, project_uuid=None, home_uuid=None):
    home = Home.objects.get(uuid=home_uuid, parent_project__uuid=project_uuid)
    project = Project.objects.get(uuid=project_uuid)
    home_users = HomeUser.objects.filter(parent_project__uuid=project_uuid, parent_home__uuid=home_uuid).all()
    context = {
        "home": home,
        "project": project,
        "home_users": home_users,
        'segment': 'home_users'
    }
    return render(request, "dashboard/home_wizard/all_home_users.html", context=context)


def create_or_edit_home_user_view(request, project_uuid=None, home_uuid=None, user_uuid=None):
    if user_uuid and project_uuid and home_uuid:
        # Edit existing project
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        home_user = get_object_or_404(HomeUser, uuid=user_uuid, parent_project__uuid=project_uuid,
                                      parent_home__uuid=home_uuid)

    else:
        # Create new home
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        home_user = None

    if request.method == "GET":
        if home_user:
            user_form = UserForm(instance=home_user.user)
            home_user_form = HomeUserForm(instance=home_user)
            return render(request, 'dashboard/home_wizard/home_user_settings.html',
                          context={'user_form': user_form, 'home_user_form': home_user_form,
                                   'project': project, 'home': home,
                                   'home_user': home_user,
                                   'form_type': 'edit_home_user'})
        else:
            user_form = UserForm()
            home_user_form = HomeUserForm()
            user_form.fields["new_password"].initial = generate_random_password()
            return render(request, 'dashboard/home_wizard/home_user_settings.html',
                          context={'user_form': user_form, 'home_user_form': home_user_form,
                                   'project': project, 'home': home,
                                   'form_type': 'create_new_home_user'})

    if request.method == "POST":
        if home_user:
            user_form = UserForm(request.POST, request.FILES, instance=home_user.user)
            home_user_form = HomeUserForm(request.POST, request.FILES, instance=home_user)
            if user_form.is_valid() and home_user_form.is_valid():
                user_instance = user_form.save(commit=True)
                home_user_instance = home_user_form.save(commit=False)
                home_user_instance.last_edited_by = request.user

                if home_user_instance.is_tablet_user == False and home_user_instance.is_web_app_user == False:
                    home_user_instance.is_tablet_user = False
                    home_user_instance.is_web_app_user = True
                home_user_instance.save()

                # 1. if in the future, we edit "create new home user" or "edit home user" pages to can edit mqtt
                # properties, we need to check mqtt properties for change. if they were changed, we need to delete
                # previous mqtt user form authenticator engine and create new one. at this moment we don't let
                # user edit these properties, So we don't need to check them.
                # 2. maybe webapp or tablet users changed by operator, So we need to
                # resend webapp or tablet user to broker(at this time web app and tablet user are identical but have
                # different entity and different set authorization rules function for future purpose.)
                if home_user_instance.is_tablet_user:
                    # delete_all_tablet_client_authorization_rules(tablet_user_uuid=home_user.uuid)
                    set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(tablet_user_uuid=home_user_instance.uuid)
                elif home_user_instance.is_web_app_user:
                    # delete_all_web_app_client_authorization_rules(home_user_uuid=home_user.uuid)
                    set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(home_user_uuid=home_user_instance.uuid)

                add_user_to_emqx_password_based_built_in_database_authentication_backend(
                    mqtt_username=home_user_instance.mqtt_username,
                    mqtt_password=home_user_instance.mqtt_password)

        else:
            user_form = UserForm(request.POST, request.FILES)
            home_user_form = HomeUserForm(request.POST, request.FILES)

            if user_form.is_valid() and home_user_form.is_valid():
                user_instance = user_form.save(commit=True)
                home_user_instance = home_user_form.save(commit=False)
                if hasattr(user_instance, 'homeUser'):
                    home_user = user_instance.homeUser
                    home_user.parent_home = home
                    home_user.parent_project = project
                    home_user.created_by = request.user
                    home_user.last_edited_by = request.user

                    if home_user_instance.is_tablet_user == False and home_user_instance.is_web_app_user == False:
                        home_user_instance.is_tablet_user = False
                        home_user_instance.is_web_app_user = True

                    add_user_to_emqx_password_based_built_in_database_authentication_backend(
                        mqtt_username=home_user_instance.mqtt_username,
                        mqtt_password=home_user_instance.mqtt_password)

                    user_instance.homeUser.save()

                    if home_user.is_tablet_user:
                        set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(tablet_user_uuid=home_user.uuid)
                    elif home_user.is_web_app_user:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(home_user_uuid=home_user.uuid)
                else:

                    if home_user_instance.is_tablet_user is False and home_user_instance.is_web_app_user is False:
                        home_user_instance.is_tablet_user = False
                        home_user_instance.is_web_app_user = True
                    home_user_instance = HomeUser.objects.create(user=user_instance,
                                                                 parent_project=project,
                                                                 parent_home=home,
                                                                 is_tablet_user=home_user_instance.is_tablet_user,
                                                                 is_web_app_user=home_user_instance.is_web_app_user,
                                                                 created_by=request.user,
                                                                 last_edited_by=request.user)

                    if home_user_instance.is_tablet_user:
                        set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(tablet_user_uuid=home_user_instance.uuid)
                    elif home_user_instance.is_web_app_user:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(home_user_uuid=home_user_instance.uuid)

                    add_user_to_emqx_password_based_built_in_database_authentication_backend(
                        mqtt_username=home_user_instance.mqtt_username,
                        mqtt_password=home_user_instance.mqtt_password)


        return redirect("dashboard:home_wizard_all_users", project_uuid=project.uuid, home_uuid=home.uuid)


def delete_home_user_view(request, project_uuid, home_uuid, user_uuid):
    if user_uuid and project_uuid and home_uuid:
        # Edit existing project
        home_user = get_object_or_404(HomeUser, uuid=user_uuid, parent_project__uuid=project_uuid,
                                      parent_home__uuid=home_uuid)
    else:
        home_user = None

    if home_user:
        delete_user_from_emqx_password_based_built_in_database_authentication_backend(mqtt_username=home_user.mqtt_username)

        if home_user.is_tablet_user:
            delete_all_tablet_client_authorization_rules(tablet_user_uuid=home_user.uuid)

        elif home_user.is_web_app_user:
            delete_all_web_app_client_authorization_rules(home_user_uuid=home_user.uuid)

        else:
            delete_all_web_app_client_authorization_rules(home_user_uuid=home_user.uuid)

        User.objects.get(id=home_user.user.id).delete()

        return redirect('dashboard:home_wizard_all_users', project_uuid, home_uuid)

    else:
        return redirect('dashboard:home_wizard_all_users', project_uuid, home_uuid)


#############################################################################################################

def home_all_controller_view(request, project_uuid=None, home_uuid=None):
    home = Home.objects.get(uuid=home_uuid, parent_project__uuid=project_uuid)
    project = Project.objects.get(uuid=project_uuid)
    controllers = Controller.objects.filter(parent_project__uuid=project_uuid, parent_home__uuid=home_uuid).all()

    context = {
        'segment': 'controllers',
        "home": home,
        "project": project,
        "controllers": controllers,
    }
    return render(request, 'dashboard/home_wizard/all_controllers.html', context=context)


def create_or_edit_home_controller_view(request, project_uuid=None, home_uuid=None, controller_uuid=None):
    if controller_uuid:
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        controller = get_object_or_404(Controller, uuid=controller_uuid, parent_project__uuid=project_uuid,
                                       parent_home__uuid=home_uuid)
    else:
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        controller = None
    if request.method == "GET":
        if controller:
            controller_form = ControllerForm(instance=controller)
            credential_controller_form = ControllerCredentialForm(instance=controller)
            context = {
                'segment': 'controllers',
                "home": home,
                "project": project,
                "controller": controller,
                "controller_form": controller_form,
                'form_type': 'edit_controller',
                'controller_credentials_form': credential_controller_form
            }
            return render(request, 'dashboard/home_wizard/controller_settings.html', context=context)
        else:
            controller_form = ControllerForm()
            context = {
                'segment': 'controllers',
                "home": home,
                "project": project,
                "controller": controller,
                "controller_form": controller_form,
                'form_type': 'create_new_controller'
            }
            return render(request, 'dashboard/home_wizard/controller_settings.html', context=context)

    if request.method == "POST":
        if controller:
            controller_form = ControllerForm(request.POST, request.FILES, instance=controller)
            if controller_form.is_valid():
                controller_instance = controller_form.save(commit=False)
                controller_instance.last_edited_by = request.user

                if controller.mqtt_username != controller_instance.mqtt_username or controller.mqtt_password != controller_instance.mqtt_password:
                    delete_user_from_emqx_password_based_built_in_database_authentication_backend(
                        mqtt_username=controller.mqtt_username)

                    add_user_to_emqx_password_based_built_in_database_authentication_backend(
                        mqtt_username=controller_instance.mqtt_username,
                        mqtt_password=controller_instance.mqtt_password)

                controller_instance.save()

                if controller.mqtt_client_id != controller_instance.mqtt_client_id:
                    status = delete_all_controller_client_authorization_rules(controller_uuid=controller.uuid)

                set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=controller_instance.uuid)

                all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                         parent_home__uuid=home.uuid).all()
                for home_user in all_home_users:
                    if home_user.is_web_app_user:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                            home_user_uuid=home_user.uuid)
                    elif home_user.is_tablet_user:
                        set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                            tablet_user_uuid=home_user.uuid)
                    else:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                            home_user_uuid=home_user.uuid)

        else:
            controller_form = ControllerForm(request.POST, request.FILES)
            if controller_form.is_valid():
                controller_instance = controller_form.save(commit=False)
                controller_instance.parent_project = project
                controller_instance.parent_home = home
                controller_instance.created_by = request.user
                controller_instance.last_edited_by = request.user

                # generate_controller_credentials()

                controller_instance.save()

                add_user_to_emqx_password_based_built_in_database_authentication_backend(
                    mqtt_username=controller_instance.mqtt_username,
                    mqtt_password=controller_instance.mqtt_password)

                set_controller_client_rule_to_emqx_built_in_database_authorization_backend(project_uuid=project.uuid,
                                                                                           home_uuid=home.uuid,
                                                                                           controller_uuid=controller_instance.uuid)

                all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                         parent_home__uuid=home.uuid).all()
                for home_user in all_home_users:
                    if home_user.is_web_app_user:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                            home_user_uuid=home_user.uuid)
                    elif home_user.is_tablet_user:
                        set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                            tablet_user_uuid=home_user.uuid)
                    else:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                            home_user_uuid=home_user.uuid)

        return redirect('dashboard:home_wizard_all_controllers', project.uuid, home.uuid)


def delete_home_controller_view(request, project_uuid=None, home_uuid=None, controller_uuid=None):
    home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
    project = get_object_or_404(Project, uuid=project_uuid)
    controller = get_object_or_404(Controller, uuid=controller_uuid, parent_project__uuid=project_uuid,
                                   parent_home__uuid=home_uuid)

    if controller and home and project:
        delete_user_from_emqx_password_based_built_in_database_authentication_backend(
            mqtt_username=controller.mqtt_username)
        delete_all_controller_client_authorization_rules(controller_uuid=controller.uuid)
        delete_count , _ = controller.delete()
        if delete_count > 0:
            all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                     parent_home__uuid=home.uuid).all()
            for home_user in all_home_users:
                if home_user.is_web_app_user:
                    set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(home_user_uuid=home_user.uuid)
                elif home_user.is_tablet_user:
                    set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(tablet_user_uuid=home_user.uuid)
                else:
                    set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                        home_user_uuid=home_user.uuid)

    return redirect('dashboard:home_wizard_all_controllers', project.uuid, home.uuid)


def download_home_controller_config_view(request, project_uuid=None, home_uuid=None, controller_uuid=None):
    pass


def home_all_devices_view(request, project_uuid=None, home_uuid=None):
    home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
    project = get_object_or_404(Project, uuid=project_uuid)
    devices = DeviceProxy.objects.filter(device_base__parent_home__uuid=home_uuid,
                                         device_base__parent_project__uuid=project_uuid).all()

    device_types = ['fourpoleswitch', 'fivepoleswitch', 'fourpolethermostat', 'tenpolethermostat']
    context = {
        'segment': 'devices',
        'home': home,
        'project': project,
        'devices': devices,
        'device_types': device_types
    }

    return render(request, 'dashboard/home_wizard/all_devices.html', context=context)


def create_or_edit_home_device_view(request, project_uuid=None, home_uuid=None, device_uuid=None):
    if device_uuid:
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        device = get_object_or_404(DeviceProxy, device_base__uuid=device_uuid,
                                   device_base__parent_project__uuid=project_uuid,
                                   device_base__parent_home__uuid=home_uuid)
    else:
        device = None
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)

    if request.method == "GET":
        selected_device_type = request.GET.get('device_type', None)
        if not device:
            if selected_device_type:
                if selected_device_type == 'fourpoleswitch':
                    four_pole_switch_form = FourPoleSwitchForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    four_pole_switch_data_point_form = fourPoleSwitch_dataPointFunction_formSet(
                        initial=four_pole_switch_data_point_function_formset_initial)
                    context = {
                        'segment': 'devices',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_device',
                        'device_type': selected_device_type,
                        'switch_form': four_pole_switch_form,
                        'switch_formset': four_pole_switch_data_point_form
                    }
                    return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

                elif selected_device_type == 'fivepoleswitch':
                    five_pole_switch_form = FivePoleSwitchForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    five_pole_switch_data_point_form = fivePoleSwitch_dataPointFunction_formSet(
                        initial=five_pole_switch_data_point_function_formset_initial)
                    context = {
                        'segment': 'devices',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_device',
                        'device_type': selected_device_type,
                        'switch_form': five_pole_switch_form,
                        'switch_formset': five_pole_switch_data_point_form
                    }
                    return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

                elif selected_device_type == 'fourpolethermostat':
                    four_pole_thermostat_form = FourPoleThermostatForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    four_pole_thermostat_data_point_form = thermostat_of_fourPoleThermostat_dataPointFunction_formSet(
                        initial=thermostat_data_point_formset_initial)
                    context = {
                        'segment': 'devices',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_device',
                        'device_type': selected_device_type,
                        'thermostat_form': four_pole_thermostat_form,
                        'thermostat_formset': four_pole_thermostat_data_point_form
                    }
                    return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

                elif selected_device_type == 'tenpolethermostat':
                    ten_pole_thermostat_form = TenPoleThermostatForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    thermostat_of_ten_pole_thermostat_data_point_form = thermostat_of_tenPoleThermostat_dataPointFunction_formSet(
                        initial=thermostat_data_point_formset_initial, prefix='thermostat_thermostat_data_point')
                    switches_of_ten_pole_thermostat_data_point_function_formset = switches_of_tenPoleThermostat_dataPointFunction_formSet(
                        initial=switches_of_ten_pole_thermostat_data_point_function_formset_initial,
                        prefix='thermostat_switches_data_point')
                    context = {
                        'segment': 'devices',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_device',
                        'device_type': selected_device_type,
                        'thermostat_form': ten_pole_thermostat_form,
                        'thermostat_formset': thermostat_of_ten_pole_thermostat_data_point_form,
                        'switch_formset': switches_of_ten_pole_thermostat_data_point_function_formset,
                    }
                    return render(request, 'dashboard/home_wizard/device_settings.html', context=context)
        else:
            device_type = device.content_type.model
            if device_type == 'fourpoleswitch':
                four_pole_switch_form = FourPoleSwitchForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                           instance=device.content_object)
                four_pole_switch_data_point_form = fourPoleSwitch_dataPointFunction_formSet(
                    instance=device.content_object)
                context = {
                    'segment': 'devices',
                    'home': home,
                    'project': project,
                    'device': device,
                    'form_type': 'edit_device',
                    'device_type': device_type,
                    'switch_form': four_pole_switch_form,
                    'switch_formset': four_pole_switch_data_point_form
                }
                return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

            elif device_type == 'fivepoleswitch':
                five_pole_switch_form = FivePoleSwitchForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                           instance=device.content_object)
                five_pole_switch_data_point_form = fivePoleSwitch_dataPointFunction_formSet(
                    instance=device.content_object)
                context = {
                    'segment': 'devices',
                    'home': home,
                    'project': project,
                    'device': device,
                    'form_type': 'edit_device',
                    'device_type': device_type,
                    'switch_form': five_pole_switch_form,
                    'switch_formset': five_pole_switch_data_point_form
                }
                return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

            elif device_type == 'fourpolethermostat':
                four_pole_thermostat_form = FourPoleThermostatForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                                   instance=device.content_object)
                four_pole_thermostat_data_point_form = thermostat_of_fourPoleThermostat_dataPointFunction_formSet(
                    instance=device.content_object)
                context = {
                    'segment': 'devices',
                    'home': home,
                    'project': project,
                    'device': device,
                    'form_type': 'edit_device',
                    'device_type': device_type,
                    'thermostat_form': four_pole_thermostat_form,
                    'thermostat_formset': four_pole_thermostat_data_point_form
                }
                return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

            elif device_type == 'tenpolethermostat':
                ten_pole_thermostat_form = TenPoleThermostatForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                                 instance=device.content_object)
                thermostat_of_ten_pole_thermostat_data_point_form = thermostat_of_tenPoleThermostat_dataPointFunction_formSet(
                    instance=device.content_object, prefix='thermostat_thermostat_data_point')
                switches_of_ten_pole_thermostat_data_point_function_formset = switches_of_tenPoleThermostat_dataPointFunction_formSet(
                    instance=device.content_object, prefix='thermostat_switches_data_point')
                context = {
                    'segment': 'devices',
                    'home': home,
                    'project': project,
                    'device': device,
                    'form_type': 'edit_device',
                    'device_type': device_type,
                    'thermostat_form': ten_pole_thermostat_form,
                    'thermostat_formset': thermostat_of_ten_pole_thermostat_data_point_form,
                    'switch_formset': switches_of_ten_pole_thermostat_data_point_function_formset,
                }
                return render(request, 'dashboard/home_wizard/device_settings.html', context=context)

    if request.method == "POST":
        post_device_type = request.GET.get('device_type', None)
        if not device:
            if post_device_type == 'fourpoleswitch':
                four_pole_switch_form = FourPoleSwitchForm(request.POST)
                if four_pole_switch_form.is_valid():
                    four_pole_switch_instance = four_pole_switch_form.save(commit=False)
                    four_pole_switch_instance.parent_project = project
                    four_pole_switch_instance.parent_home = home
                    four_pole_switch_instance.created_by = request.user
                    four_pole_switch_instance.last_edited_by = request.user
                    four_pole_switch_instance.save()
                    DeviceProxy.objects.create(device_base=four_pole_switch_instance,
                                               content_type=ContentType.objects.get_for_model(FourPoleSwitch),
                                               object_id=four_pole_switch_instance.id)
                    four_pole_switch_data_point_form = fourPoleSwitch_dataPointFunction_formSet(request.POST,
                                                                                                instance=four_pole_switch_instance)
                    if four_pole_switch_data_point_form.is_valid():
                        four_pole_switch_data_point_form.save(commit=True)

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(project_uuid=project.uuid,
                                                                                               home_uuid=home.uuid,
                                                                                               controller_uuid=four_pole_switch_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_device_type == 'fivepoleswitch':
                five_pole_switch_form = FivePoleSwitchForm(request.POST)
                if five_pole_switch_form.is_valid():
                    five_pole_switch_instance = five_pole_switch_form.save(commit=False)
                    five_pole_switch_instance.parent_project = project
                    five_pole_switch_instance.parent_home = home
                    five_pole_switch_instance.created_by = request.user
                    five_pole_switch_instance.last_edited_by = request.user
                    five_pole_switch_instance.save()
                    DeviceProxy.objects.create(device_base=five_pole_switch_instance,
                                               content_type=ContentType.objects.get_for_model(FivePoleSwitch),
                                               object_id=five_pole_switch_instance.id)
                    five_pole_switch_data_point_form = fourPoleSwitch_dataPointFunction_formSet(request.POST,
                                                                                                instance=five_pole_switch_instance)
                    if five_pole_switch_data_point_form.is_valid():
                        five_pole_switch_data_point_form.save(commit=True)

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=five_pole_switch_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_device_type == 'fourpolethermostat':
                four_pole_thermostat_form = FourPoleThermostatForm(request.POST)
                if four_pole_thermostat_form.is_valid():
                    four_pole_thermostat_instance = four_pole_thermostat_form.save(commit=False)
                    four_pole_thermostat_instance.parent_project = project
                    four_pole_thermostat_instance.parent_home = home
                    four_pole_thermostat_instance.created_by = request.user
                    four_pole_thermostat_instance.last_edited_by = request.user
                    four_pole_thermostat_instance.save()
                    DeviceProxy.objects.create(device_base=four_pole_thermostat_instance,
                                               content_type=ContentType.objects.get_for_model(FourPoleThermostat),
                                               object_id=four_pole_thermostat_instance.id)
                    four_pole_thermostat_data_point_form = thermostat_of_fourPoleThermostat_dataPointFunction_formSet(
                        request.POST,
                        instance=four_pole_thermostat_instance)
                    if four_pole_thermostat_data_point_form.is_valid():
                        four_pole_thermostat_data_point_form.save()

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=four_pole_thermostat_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_device_type == 'tenpolethermostat':
                ten_pole_thermostat_form = TenPoleThermostatForm(request.POST)
                if ten_pole_thermostat_form.is_valid():
                    ten_pole_thermostat_instance = ten_pole_thermostat_form.save(commit=False)
                    ten_pole_thermostat_instance.parent_project = project
                    ten_pole_thermostat_instance.parent_home = home
                    ten_pole_thermostat_instance.created_by = request.user
                    ten_pole_thermostat_instance.last_edited_by = request.user
                    ten_pole_thermostat_instance.save()
                    DeviceProxy.objects.create(device_base=ten_pole_thermostat_instance,
                                               content_type=ContentType.objects.get_for_model(TenPoleThermostat),
                                               object_id=ten_pole_thermostat_instance.id)

                    thermostat_of_ten_pole_thermostat_data_point_form = thermostat_of_tenPoleThermostat_dataPointFunction_formSet(
                        request.POST,
                        instance=ten_pole_thermostat_instance,
                        prefix='thermostat_thermostat_data_point')
                    switches_of_ten_pole_thermostat_data_point_form = switches_of_tenPoleThermostat_dataPointFunction_formSet(
                        request.POST,
                        instance=ten_pole_thermostat_instance,
                        prefix='thermostat_switches_data_point')

                    if thermostat_of_ten_pole_thermostat_data_point_form.is_valid() and switches_of_ten_pole_thermostat_data_point_form.is_valid():
                        thermostat_of_ten_pole_thermostat_data_point_form.save()
                        switches_of_ten_pole_thermostat_data_point_form.save()

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=ten_pole_thermostat_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

        else:
            if post_device_type == 'fourpoleswitch':
                four_pole_switch_form = FourPoleSwitchForm(request.POST, instance=device.device_base)
                if four_pole_switch_form.is_valid():
                    four_pole_switch_instance = four_pole_switch_form.save(commit=False)
                    four_pole_switch_instance.last_edited_by = request.user
                    four_pole_switch_instance.save()

                    four_pole_switch_data_point_form = fourPoleSwitch_dataPointFunction_formSet(request.POST,
                                                                                                instance=four_pole_switch_instance)
                    if four_pole_switch_data_point_form.is_valid():
                        four_pole_switch_data_point_form.save(commit=True)

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=four_pole_switch_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_device_type == 'fivepoleswitch':
                five_pole_switch_form = FivePoleSwitchForm(request.POST, instance=device.device_base)
                if five_pole_switch_form.is_valid():
                    five_pole_switch_instance = five_pole_switch_form.save(commit=False)
                    five_pole_switch_instance.last_edited_by = request.user
                    five_pole_switch_instance.save()

                    five_pole_switch_data_point_form = fourPoleSwitch_dataPointFunction_formSet(request.POST,
                                                                                                instance=five_pole_switch_instance)
                    if five_pole_switch_data_point_form.is_valid():
                        five_pole_switch_data_point_form.save(commit=True)

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=five_pole_switch_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_device_type == 'fourpolethermostat':
                four_pole_thermostat_form = FourPoleThermostatForm(request.POST, instance=device.device_base)
                if four_pole_thermostat_form.is_valid():
                    four_pole_thermostat_instance = four_pole_thermostat_form.save(commit=False)
                    four_pole_thermostat_instance.last_edited_by = request.user
                    four_pole_thermostat_instance.save()

                    four_pole_thermostat_data_point_form = thermostat_of_fourPoleThermostat_dataPointFunction_formSet(
                        request.POST,
                        instance=four_pole_thermostat_instance)
                    if four_pole_thermostat_data_point_form.is_valid():
                        four_pole_thermostat_data_point_form.save()

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=four_pole_thermostat_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_device_type == 'tenpolethermostat':
                ten_pole_thermostat_form = TenPoleThermostatForm(request.POST, instance=device.device_base)
                if ten_pole_thermostat_form.is_valid():
                    ten_pole_thermostat_instance = ten_pole_thermostat_form.save(commit=False)
                    ten_pole_thermostat_instance.last_edited_by = request.user
                    ten_pole_thermostat_instance.save()

                    thermostat_of_ten_pole_thermostat_data_point_form = thermostat_of_tenPoleThermostat_dataPointFunction_formSet(
                        request.POST,
                        instance=ten_pole_thermostat_instance,
                        prefix='thermostat_thermostat_data_point')
                    switches_of_ten_pole_thermostat_data_point_function_formset = switches_of_tenPoleThermostat_dataPointFunction_formSet(
                        request.POST,
                        instance=ten_pole_thermostat_instance,
                        prefix='thermostat_switches_data_point')

                    if thermostat_of_ten_pole_thermostat_data_point_form.is_valid() and switches_of_ten_pole_thermostat_data_point_function_formset.is_valid():
                        thermostat_of_ten_pole_thermostat_data_point_form.save()
                        switches_of_ten_pole_thermostat_data_point_function_formset.save()

                    set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                        project_uuid=project.uuid,
                        home_uuid=home.uuid,
                        controller_uuid=ten_pole_thermostat_instance.parent_controller.uuid)

                    all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                             parent_home__uuid=home.uuid).all()
                    for home_user in all_home_users:
                        if home_user.is_web_app_user:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)
                        elif home_user.is_tablet_user:
                            set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                                tablet_user_uuid=home_user.uuid)
                        else:
                            set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                                home_user_uuid=home_user.uuid)

                return redirect('dashboard:home_wizard_all_devices', project_uuid=project.uuid, home_uuid=home.uuid)


def delete_home_device_view(request, project_uuid=None, home_uuid=None, device_uuid=None):
    home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
    project = get_object_or_404(Project, uuid=project_uuid)
    device = get_object_or_404(DeviceBase, uuid=device_uuid,
                               parent_project__uuid=project_uuid,
                               parent_home__uuid=home_uuid)
    if device and home and project:
        with transaction.atomic():
            controller_uuid = device.parent_controller.uuid
            delete_count, _ = device.delete()
            if delete_count > 0:
                set_controller_client_rule_to_emqx_built_in_database_authorization_backend(
                    project_uuid=project.uuid,
                    home_uuid=home.uuid,
                    controller_uuid=controller_uuid)

                all_home_users = HomeUser.objects.filter(parent_project__uuid=project.uuid,
                                                         parent_home__uuid=home.uuid).all()
                for home_user in all_home_users:
                    if home_user.is_web_app_user:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                            home_user_uuid=home_user.uuid)
                    elif home_user.is_tablet_user:
                        set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(
                            tablet_user_uuid=home_user.uuid)
                    else:
                        set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(
                            home_user_uuid=home_user.uuid)

    return redirect('dashboard:home_wizard_all_devices', project.uuid, home.uuid)


def home_all_ui_elements_view(request, project_uuid=None, home_uuid=None):
    home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
    project = get_object_or_404(Project, uuid=project_uuid)
    ui_elements = UIProxy.objects.filter(ui_base__parent_project__uuid=project_uuid,
                                         ui_base__parent_home__uuid=home_uuid).all()

    ui_element_types = {'switchui': 'Switch Button UI', 'pushbuttonui': 'Push Button UI',
                        'thermostatui': 'Thermostat Button UI', 'curtainui': 'Curtain Button UI'}
    context = {
        'segment': 'ui',
        'home': home,
        'project': project,
        'ui_elements': ui_elements,
        'ui_element_types': ui_element_types
    }
    return render(request, 'dashboard/home_wizard/all_ui.html', context=context)


def create_or_edit_home_ui_element_view(request, project_uuid=None, home_uuid=None, ui_element_uuid=None):
    if ui_element_uuid:
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)
        ui_element = get_object_or_404(UIProxy, ui_base__uuid=ui_element_uuid,
                                       ui_base__parent_project__uuid=project_uuid,
                                       ui_base__parent_home__uuid=home_uuid)
    else:
        ui_element = None
        home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
        project = get_object_or_404(Project, uuid=project_uuid)

    if request.method == "GET":
        selected_ui_element_type = request.GET.get('ui_element_type', None)
        if not ui_element:
            if selected_ui_element_type:
                if selected_ui_element_type == 'switchui':
                    switch_ui_form = SwitchUIForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    context = {
                        'segment': 'ui',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_ui_element',
                        'ui_element_type': selected_ui_element_type,
                        'form': switch_ui_form
                    }
                    return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

                elif selected_ui_element_type == 'pushbuttonui':
                    push_button_ui_form = PushButtonUIForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    context = {
                        'segment': 'ui',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_ui_element',
                        'ui_element_type': selected_ui_element_type,
                        'form': push_button_ui_form,
                    }
                    return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

                elif selected_ui_element_type == 'thermostatui':
                    thermostat_ui_form = ThermostatUIForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    context = {
                        'segment': 'ui',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_ui_element',
                        'ui_element_type': selected_ui_element_type,
                        'form': thermostat_ui_form,

                    }
                    return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

                elif selected_ui_element_type == 'curtainui':
                    curtain_ui_form = CurtainUIForm(home_uuid=home.uuid, project_uuid=project.uuid)
                    context = {
                        'segment': 'ui',
                        'home': home,
                        'project': project,
                        'form_type': 'create_new_ui_element',
                        'ui_element_type': selected_ui_element_type,
                        'form': curtain_ui_form,
                    }
                    return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)
        else:
            ui_element_type = ui_element.content_type.model
            if ui_element_type == 'switchui':
                switch_ui_form = SwitchUIForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                              instance=ui_element.content_object)
                context = {
                    'segment': 'ui',
                    'home': home,
                    'project': project,
                    'ui_element': ui_element,
                    'form_type': 'edit_ui_element',
                    'ui_element_type': ui_element_type,
                    'form': switch_ui_form,
                }
                return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

            elif ui_element_type == 'pushbuttonui':
                push_button_ui_form = PushButtonUIForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                       instance=ui_element.content_object)

                context = {
                    'segment': 'ui',
                    'home': home,
                    'project': project,
                    'ui_element': ui_element,
                    'form_type': 'edit_ui_element',
                    'ui_element_type': ui_element_type,
                    'form': push_button_ui_form,

                }
                return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

            elif ui_element_type == 'thermostatui':
                thermostat_ui_form = ThermostatUIForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                      instance=ui_element.content_object)
                context = {
                    'segment': 'ui',
                    'home': home,
                    'project': project,
                    'ui_element': ui_element,
                    'form_type': 'edit_ui_element',
                    'ui_element_type': ui_element_type,
                    'form': thermostat_ui_form,
                }
                return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

            elif ui_element_type == 'curtainui':
                curtain_ui_form = CurtainUIForm(home_uuid=home.uuid, project_uuid=project.uuid,
                                                instance=ui_element.content_object)

                context = {
                    'segment': 'ui',
                    'home': home,
                    'project': project,
                    'ui_element': ui_element,
                    'form_type': 'edit_ui_element',
                    'ui_element_type': ui_element_type,
                    'form': curtain_ui_form,

                }
                return render(request, 'dashboard/home_wizard/ui_settings.html', context=context)

    if request.method == "POST":
        post_ui_element_type = request.GET.get('ui_element_type', None)
        if not ui_element:
            if post_ui_element_type == 'switchui':
                switch_button_ui_form = SwitchUIForm(request.POST)
                if switch_button_ui_form.is_valid():
                    switch_ui_element_instance = switch_button_ui_form.save(commit=False)
                    switch_ui_element_instance.parent_project = project
                    switch_ui_element_instance.parent_home = home
                    switch_ui_element_instance.created_by = request.user
                    switch_ui_element_instance.last_edited_by = request.user
                    switch_ui_element_instance.save()
                    UIProxy.objects.create(ui_base=switch_ui_element_instance,
                                           content_type=ContentType.objects.get_for_model(SwitchUI),
                                           object_id=switch_ui_element_instance.id)

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_ui_element_type == 'pushbuttonui':
                push_button_ui_form = PushButtonUIForm(request.POST)
                if push_button_ui_form.is_valid():
                    push_button_ui_element_instance = push_button_ui_form.save(commit=False)
                    push_button_ui_element_instance.parent_project = project
                    push_button_ui_element_instance.parent_home = home
                    push_button_ui_element_instance.created_by = request.user
                    push_button_ui_element_instance.last_edited_by = request.user
                    push_button_ui_element_instance.save()
                    UIProxy.objects.create(ui_base=push_button_ui_element_instance,
                                           content_type=ContentType.objects.get_for_model(PushButtonUI),
                                           object_id=push_button_ui_element_instance.id)

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_ui_element_type == 'thermostatui':
                thermostat_ui_form = ThermostatUIForm(request.POST)
                if thermostat_ui_form.is_valid():
                    thermostat_ui_element_instance = thermostat_ui_form.save(commit=False)
                    thermostat_ui_element_instance.parent_project = project
                    thermostat_ui_element_instance.parent_home = home
                    thermostat_ui_element_instance.created_by = request.user
                    thermostat_ui_element_instance.last_edited_by = request.user
                    thermostat_ui_element_instance.save()
                    UIProxy.objects.create(ui_base=thermostat_ui_element_instance,
                                           content_type=ContentType.objects.get_for_model(ThermostatUI),
                                           object_id=thermostat_ui_element_instance.id)

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_ui_element_type == 'curtainui':
                curtain_ui_form = CurtainUIForm(request.POST)
                if curtain_ui_form.is_valid():
                    curtain_ui_element_instance = curtain_ui_form.save(commit=False)
                    curtain_ui_element_instance.parent_project = project
                    curtain_ui_element_instance.parent_home = home
                    curtain_ui_element_instance.created_by = request.user
                    curtain_ui_element_instance.last_edited_by = request.user
                    curtain_ui_element_instance.save()
                    UIProxy.objects.create(ui_base=curtain_ui_element_instance,
                                           content_type=ContentType.objects.get_for_model(CurtainUI),
                                           object_id=curtain_ui_element_instance.id)

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

        else:
            if post_ui_element_type == 'switchui':
                switch_ui_form = SwitchUIForm(request.POST, instance=ui_element.content_object)
                if switch_ui_form.is_valid():
                    switch_ui_element_instance = switch_ui_form.save(commit=False)
                    switch_ui_element_instance.last_edited_by = request.user
                    switch_ui_element_instance.save()

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_ui_element_type == 'pushbuttonui':
                push_button_ui_form = PushButtonUIForm(request.POST, instance=ui_element.content_object)
                if push_button_ui_form.is_valid():
                    push_button_ui_element_instance = push_button_ui_form.save(commit=False)
                    push_button_ui_element_instance.last_edited_by = request.user
                    push_button_ui_element_instance.save()

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_ui_element_type == 'thermostatui':
                thermostat_ui_form = ThermostatUIForm(request.POST, instance=ui_element.content_object)
                if thermostat_ui_form.is_valid():
                    thermostat_ui_element_instance = thermostat_ui_form.save(commit=False)
                    thermostat_ui_element_instance.last_edited_by = request.user
                    thermostat_ui_element_instance.save()

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)

            elif post_ui_element_type == 'curtainui':
                curtain_ui_form = CurtainUIForm(request.POST, instance=ui_element.content_object)
                if curtain_ui_form.is_valid():
                    curtain_ui_element_instance = curtain_ui_form.save(commit=False)
                    curtain_ui_element_instance.last_edited_by = request.user
                    curtain_ui_element_instance.save()

                return redirect('dashboard:home_wizard_all_ui_elements', project_uuid=project.uuid, home_uuid=home.uuid)


def delete_home_ui_element_view(request, project_uuid=None, home_uuid=None, ui_element_uuid=None):
    home = get_object_or_404(Home, uuid=home_uuid, parent_project__uuid=project_uuid)
    project = get_object_or_404(Project, uuid=project_uuid)
    ui_element = get_object_or_404(UIBase, uuid=ui_element_uuid,
                                   parent_project__uuid=project_uuid,
                                   parent_home__uuid=home_uuid)
    if ui_element and home and project:
        ui_element.delete()

    return redirect('dashboard:home_wizard_all_ui_elements', project.uuid, home.uuid)


############### MQTT manager ###################

# Example usage in a Django view
# def my_view(request):
    # Publish a message
def handle_message(topic: str, payload: Any):
    print(f"Received message on {topic}: {payload}")
    # Process the message as needed


initialize_mqtt()

# publish_message("test/topic", {"message": "Hello from Django!"})

# Subscribe to a topic
# subscribe_to_topic("test/topic", handle_message)

# Your view logic here
# return HttpResponse("MQTT message published and subscribed!")





# from .mqtt_manager_v2 import mqtt_manager
#
#
# def handle_message(topic: str, payload: Any):
#     print(f"Received message on {topic}: {payload}")
#     # Process the message as needed
#
#
# mqtt_manager.publish("test/topic", {"message": "Hello from Django!"})
# mqtt_manager.subscribe("test/topic", handle_message)

############### Users Section ##################


def dashboard_all_user_view(request):
    pass


def dashboard_create_new_user_view(request):
    pass


def dashboard_selected_user_view(request):
    if request.method == "GET":
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


############### login/logout section ##################


def sign_in_view(request):
    pass


def sign_out_view(request):
    pass


def amir(request):
    # Define the context you want to pass to the template
    # Render the template to a string

    rendered_template = render_to_string('amir.html', {'request': request.headers})

    # Return the rendered template as a string in a JSON response
    return JsonResponse({'rendered_template': rendered_template})


def settings(request):
    context = {
        'parent': 'extra',
        'segment': 'settings',
    }
    return render(request, 'dashboard/home_settings.html', context)


def settings_button(request):
    context = {
        'parent': 'extra',
        'segment': 'settings',
    }
    rendered_template = render_to_string('settings_button.html', context)
    return JsonResponse({'rendered_template': rendered_template})


def font(request):
    if request.method == 'POST':
        formset = DeviceSwitchActionsFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('some_success_url')
    else:
        return render(request, 'experimental/fontawesome_selector_v2.html')


from .forms import DeviceSwitchActionsFormSet


def manage_device_switch_actions(request):
    if request.method == 'POST':
        formset = DeviceSwitchActionsFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('some_success_url')
    else:
        formset = DeviceSwitchActionsFormSet(queryset=DeviceSwitchActions.objects.none())

    return render(request, 'experimental/actionFroms.html', {'formset': formset})


def manage_multiple_device_switch_actions(request):
    if request.method == 'POST':
        formset1 = DeviceSwitchActionsFormSet(request.POST, prefix='switch')
        formset2 = DeviceSwitchActionsFormSet(request.POST, prefix='status')
        if formset1.is_valid() and formset1.is_valid():
            formset1.save()
            return redirect('some_success_url')
    else:
        formset1 = DeviceSwitchActionsFormSet(queryset=DeviceSwitchActions.objects.none(), prefix='switch')
        formset2 = DeviceSwitchActionsFormSet(queryset=DeviceSwitchActions.objects.none(), prefix='status')

    return render(request, 'experimental/actionForm_2.html', {'switch': formset1, 'status': formset2})


def manage_device_actions(request):
    specific_ref_data_point = DataPointFunction.objects.get(id=1)
    if request.method == 'POST':
        switch_formset = DeviceSwitchActionsFormSet(request.POST, prefix='switch')
        status_formset = DeviceSwitchActionsFormSet(request.POST, prefix='status')

        if switch_formset.is_valid() and status_formset.is_valid():
            switch_formset.save()
            status_formset.save()
            return redirect('some_success_url')
    else:
        switch_formset = DeviceSwitchActionsFormSet(queryset=DeviceSwitchActions.objects.none(), prefix='switch')
        for form in switch_formset:
            form.fields['ref_data_point'].initial = specific_ref_data_point.id
        status_formset = DeviceSwitchActionsFormSet(queryset=DeviceSwitchActions.objects.none(), prefix='status')

    return render(request, 'experimental/actionForm_2.html', {
        'switch_formset': switch_formset,
        'status_formset': status_formset
    })


from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Permission
from django.contrib.auth import login
from .forms import CustomUserCreationForm, UserPermissionsForm


def create_user(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        permissions_form = UserPermissionsForm(request.POST)
        if user_form.is_valid() and permissions_form.is_valid():
            user = user_form.save()
            permissions = permissions_form.cleaned_data['permissions']
            user.user_permissions.set(permissions)
            user.save()
            login(request, user)  # Optionally log the user in
            return redirect('user_list')  # Redirect to a user list or another page
    else:
        user_form = CustomUserCreationForm()
        permissions_form = UserPermissionsForm()

    return render(request, 'experimental/user_creation.html', {
        'user_form': user_form,
        'permissions_form': permissions_form
    })
