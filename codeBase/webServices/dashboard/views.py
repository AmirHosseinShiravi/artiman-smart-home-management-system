from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse


# Create your views here.


############## Projects Section ###############

def all_projects_view(request):
    pass


def create_new_project(request):
    if request.method == "GET":
        # to send "new project page".
        pass
    if request.method == "POST":
        # to get new project datas and save them.
        pass


def selected_project_view(request):
    if request.method == "GET":
        # only show project properties page and not open all home related to it page.
        # we have another button for this purpose(to open all project homes).
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


############### Project Homes Section ###############

def project_all_homes_view(request):
    pass


def create_new_home(request):
    if request.method == "GET":
        # to send "new home page".
        pass
    if request.method == "POST":
        # to get "create new home" datas and save them.
        pass


def selected_home_view(request):
    if request.method == "GET":
        # unlike get method in selected_project_view view, we use this method to load home settings page.
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


############### Home Section ##################

def view_selected_home_settings_page(request):
    # show page loader when switch between menu links.
    pass


def home_general_settings_section_view(request):
    if request.method == "POST":
        pass
    if request.method == "GET":
        pass
    if request.method == "DELETE":
        pass


def home_all_controller_view(request):
    pass


def home_controller_settings_view(request):
    if request.method == "GET":
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


def home_all_devices_view(request):
    pass


def home_device_settings_view(request):
    if request.method == "GET":
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


def home_all_zones_view(request):
    pass


def home_zone_settings_view(request):
    if request.method == "GET":
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


def home_all_users_view(request):
    pass


def home_user_settings_view(request):
    if request.method == "GET":
        pass
    if request.method == "POST":
        pass
    if request.method == "DELETE":
        pass


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
    rendered_template = render_to_string('amir.html')

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

