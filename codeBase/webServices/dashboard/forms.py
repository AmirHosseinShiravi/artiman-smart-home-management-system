import os
from copy import deepcopy

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, modelformset_factory, formset_factory
from django.contrib.auth.models import User, Group

from core import settings
from .models import Project, Home, HomeUser, Tablet, Controller, Zone, \
    DeviceBase, DataPointFunction, SwitchDataPointFunction, ThermostatDataPointFunction, Switch, \
    FourPoleSwitch, FivePoleSwitch, Thermostat, FourPoleThermostat, TenPoleThermostat, \
    DeviceSwitchActions, UIBase, UIProxy, SwitchUI, PushButtonUI, CurtainUI, ThermostatUI, DashboardUser

from .utils import generate_random_username, generate_random_password


# custom image widget
from django.forms import ClearableFileInput
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _




from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "username"}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "password"}),
    )
  



class DashboardBaseUserForm(forms.ModelForm):
    # new_password = forms.CharField(required=False, label='New Password', initial=generate_random_password)
    new_password = forms.CharField(required=False, label='New Password')
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(DashboardBaseUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = generate_random_username(length=12)
        for field in self.fields.values():
            # if field.label == 'active':
            #     field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            # else:
            if field.label == 'Username':
                field.widget.attrs.update({'class': 'form-control'})
            elif field.label == 'First name':
                field.widget.attrs.update({'class': 'form-control'})
            elif field.label == 'Last name':
                field.widget.attrs.update({'class': 'form-control'})
            elif field.label == 'Email address':
                field.widget.attrs.update({'class': 'form-control'})
            elif field.label == 'New Password':
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['new_password']:
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user



class DashboardUserForm(forms.ModelForm):
    # group = forms.ModelChoiceField(label='Group', queryset=Group.objects.all())
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file d-none'}), required=False)
    class Meta:
        model = DashboardUser
        fields = ['telegramID', 'group']
    
    def __init__(self, *args, **kwargs):
        super(DashboardUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():

            if field.label == 'TelegramID':
                field.widget.attrs.update({'class': 'form-control'})
            elif field.label == 'Group':
                field.widget.attrs.update({'class': 'form-select'})
                field.queryset = Group.objects.all()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'owner_name', 'owner_phone_number', 'descriptions', 'city', 'address',
                  'status', 'project_lock']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label != "Project lock":
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})


class HomeForm(forms.ModelForm):
    class Meta:
        model = Home
        fields = ['home_name', 'owner_name', 'owner_phone_number', 'building', 'floor', 'unit', 'descriptions']

    def __init__(self, *args, **kwargs):
        super(HomeForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class TabletForm(forms.ModelForm):
    class Meta:
        model = Tablet
        fields = ['status', 'descriptions', 'tablet_has_internal_mqtt_broker', 'tablet_ip_address',
                  'tablet_internal_mqtt_broker_port', 'tablet_internal_mqtt_broker_username',
                  'tablet_internal_mqtt_broker_password']

    def __init__(self, *args, **kwargs):
        super(TabletForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label == 'Status':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            elif field.label == 'Tablet has internal mqtt broker':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class UserForm(forms.ModelForm):
    # new_password = forms.CharField(required=False, label='New Password', initial=generate_random_password)
    new_password = forms.CharField(required=False, label='New Password')
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = generate_random_username(length=12)
        for field in self.fields.values():
            # if field.label == 'active':
            #     field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            # else:
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['new_password']:
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user


class CustomImageWidget(ClearableFileInput):
    template_name = os.path.join(settings.BASE_DIR, 'templates', 'widgets', 'custom_image_widget.html')

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'is_initial': self.is_initial(value),
            'input_text': _('Change'),
            'initial_text': _('Image'),
            'clear_checkbox_label': _('Clear'),
        })
        return context


class HomeUserForm(forms.ModelForm):
    class Meta:
        model = HomeUser
        fields = ['desc', 'avatar', 'is_tablet_user', 'is_web_app_user']
        # widgets = {
        #     'avatar': CustomImageWidget(),
        # }

    def __init__(self, *args, **kwargs):
        super(HomeUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label == 'Is tablet user':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            elif field.label == 'Is web app user':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['zone_name', 'description']

    def __init__(self, *args, **kwargs):
        super(ZoneForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ControllerForm(forms.ModelForm):
    class Meta:
        model = Controller
        fields = ['name', 'descriptions', 'enable_internal_server', 'ip_address', 'port_number', 'uart_baud_rate',
                  'mqtt_client_id', 'mqtt_username', 'mqtt_password']

    def __init__(self, *args, **kwargs):
        super(ControllerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label == 'Enable internal server':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class ControllerCredentialForm(forms.ModelForm):
    class Meta:
        model = Controller
        fields = ['client_key_pem', 'client_cert_pem']

    def __init__(self, *args, **kwargs):
        super(ControllerCredentialForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control', 'disabled': ''})


class DeviceBaseForm(forms.ModelForm):
    class Meta:
        model = DeviceBase
        fields = ['name', 'descriptions', 'parent_zone', 'parent_controller', 'modbus_id']

    def __init__(self, *args, **kwargs):
        home_uuid = kwargs.get('home_uuid', None)
        if home_uuid:
            del kwargs['home_uuid']
        project_uuid = kwargs.get('project_uuid', None)
        if project_uuid:
            del kwargs['project_uuid']

        super(DeviceBaseForm, self).__init__(*args, **kwargs)

        if home_uuid and project_uuid:
            self.fields['parent_zone'].queryset = Zone.objects.filter(parent_home__uuid=home_uuid,
                                                                      parent_project__uuid=project_uuid).all()
            self.fields['parent_controller'].queryset = Controller.objects.filter(parent_home__uuid=home_uuid,
                                                                            parent_project__uuid=project_uuid).all()
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class DataPointFunctionForm(forms.ModelForm):
    class Meta:
        model = DataPointFunction
        fields = ['display_name', 'function_name', 'value', 'value_type']


class SwitchFunctionForm(forms.ModelForm):
    class Meta:
        model = SwitchDataPointFunction
        fields = ['display_name', 'function_name', 'value_type', 'switch_id']

    def __init__(self, *args, **kwargs):
        super(SwitchFunctionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ThermostatFunctionForm(forms.ModelForm):
    class Meta:
        model = ThermostatDataPointFunction
        fields = ['display_name', 'function_name', 'value_type']

    def __init__(self, *args, **kwargs):
        super(ThermostatFunctionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class FourPoleSwitchForm(DeviceBaseForm):
    class Meta(DeviceBaseForm.Meta):
        model = FourPoleSwitch
        fields = DeviceBaseForm.Meta.fields  # Plus any additional fields if necessary


class FivePoleSwitchForm(DeviceBaseForm):
    class Meta(DeviceBaseForm.Meta):
        model = FivePoleSwitch
        fields = DeviceBaseForm.Meta.fields  # Plus any additional fields if necessary


class ThermostatForm(DeviceBaseForm):
    class Meta(DeviceBaseForm.Meta):
        model = Thermostat
        fields = DeviceBaseForm.Meta.fields


class FourPoleThermostatForm(DeviceBaseForm):
    class Meta(DeviceBaseForm.Meta):
        model = FourPoleThermostat
        fields = DeviceBaseForm.Meta.fields


class TenPoleThermostatForm(DeviceBaseForm):
    class Meta(DeviceBaseForm.Meta):
        model = TenPoleThermostat
        fields = DeviceBaseForm.Meta.fields



# class DeviceSwitchActionsForm(forms.ModelForm):
#     class Meta:
#         model = DeviceSwitchActions
#         fields = []


class DeviceSwitchActionsForm(forms.ModelForm):
    ref_data_point = forms.ModelChoiceField(queryset=DataPointFunction.objects.all())
    target_data_point = forms.ModelChoiceField(queryset=DataPointFunction.objects.all())

    class Meta:
        model = DeviceSwitchActions
        fields = ['ref_data_point', 'ref_data_point_status', 'target_data_point', 'target_data_point_status', 'target_data_point_status_type']

    def __init__(self, *args, **kwargs):
        super(DeviceSwitchActionsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control m-3'})


DeviceSwitchActionsFormSet = modelformset_factory(DeviceSwitchActions, form=DeviceSwitchActionsForm, extra=1)


class UIBaseForm(forms.ModelForm):
    class Meta:
        model = UIBase
        fields = ['name', 'descriptions', 'parent_zone', 'button_name', 'on_icon', 'off_icon', 'on_text', 'off_text',
                  'on_color', 'off_color', 'add_to_home']

    def __init__(self, *args, **kwargs):
        home_uuid = kwargs.get('home_uuid', None)
        if home_uuid:
            del kwargs['home_uuid']
        project_uuid = kwargs.get('project_uuid', None)
        if project_uuid:
            del kwargs['project_uuid']

        super(UIBaseForm, self).__init__(*args, **kwargs)

        if home_uuid and project_uuid:
            self.fields['parent_zone'].queryset = Zone.objects.filter(parent_home__uuid=home_uuid,
                                                                      parent_project__uuid=project_uuid).all()




class SwitchUIForm(UIBaseForm):
    class Meta:
        model = SwitchUI
        child_fields = deepcopy(UIBaseForm.Meta.fields)
        child_fields.insert(4, 'data_point_function')
        child_fields.remove('on_color')
        child_fields.remove('off_color')
        fields = child_fields

    def __init__(self, *args, **kwargs):
        home_uuid = kwargs.get('home_uuid', None)
        project_uuid = kwargs.get('project_uuid', None)

        super(SwitchUIForm, self).__init__(*args, **kwargs)

        if home_uuid and project_uuid:
            self.fields['data_point_function'].queryset = SwitchDataPointFunction.objects.filter(device_base__parent_home__uuid=home_uuid,
                                                                                                 device_base__parent_project__uuid=project_uuid).all()
        for field_name, field in self.fields.items():
            if field_name == 'add_to_home':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            elif field_name == 'off_color':
                field.widget.attrs.update({'id': 'colorpicker-off-color', 'class': 'form-control coloris instance1', 'value': '#45aaf2'})
            elif field_name == 'on_color':
                field.widget.attrs.update({'id': 'colorpicker-on-color',  'class': 'form-control coloris instance2', 'value': '#45aaf2'})
            elif field_name == 'on_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            elif field_name == 'off_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class PushButtonUIForm(UIBaseForm):
    class Meta:
        model = PushButtonUI
        child_fields = deepcopy(UIBaseForm.Meta.fields)
        child_fields.insert(4, 'data_point_function')
        child_fields.remove('on_color')
        child_fields.remove('off_color')
        fields = child_fields

    def __init__(self, *args, **kwargs):
        home_uuid = kwargs.get('home_uuid', None)
        project_uuid = kwargs.get('project_uuid', None)

        super(PushButtonUIForm, self).__init__(*args, **kwargs)

        if home_uuid and project_uuid:
            self.fields['data_point_function'].queryset = SwitchDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()

        for field_name, field in self.fields.items():
            if field_name == 'add_to_home':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            elif field_name == 'off_color':
                field.widget.attrs.update(
                    {'id': 'colorpicker-off-color', 'class': 'form-control coloris instance1', 'value': '#45aaf2'})
            elif field_name == 'on_color':
                field.widget.attrs.update(
                    {'id': 'colorpicker-on-color', 'class': 'form-control coloris instance2', 'value': '#45aaf2'})
            elif field_name == 'on_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            elif field_name == 'off_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class CurtainUIForm(UIBaseForm):
    class Meta:
        model = CurtainUI
        child_fields = deepcopy(UIBaseForm.Meta.fields)
        child_fields.insert(4, 'open_data_point_function')
        child_fields.insert(5, 'close_data_point_function')
        child_fields.insert(6, 'animation_duration')
        # remove on_color and off_color from child_fields
        child_fields.remove('on_color')
        child_fields.remove('off_color')
        fields = child_fields

    def __init__(self, *args, **kwargs):
        home_uuid = kwargs.get('home_uuid', None)
        project_uuid = kwargs.get('project_uuid', None)

        super(CurtainUIForm, self).__init__(*args, **kwargs)

        if home_uuid and project_uuid:
            self.fields['open_data_point_function'].queryset = SwitchDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()
            self.fields['close_data_point_function'].queryset = SwitchDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()

        for field_name, field in self.fields.items():
            if field_name == 'add_to_home':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            elif field_name == 'off_color':
                field.widget.attrs.update(
                    {'id': 'colorpicker-off-color', 'class': 'form-control coloris instance1', 'value': '#45aaf2'})
            elif field_name == 'on_color':
                field.widget.attrs.update(
                    {'id': 'colorpicker-on-color', 'class': 'form-control coloris instance2', 'value': '#45aaf2'})
            # elif field_name == 'on_icon':
            #     field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            # elif field_name == 'off_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            elif field_name == 'animation_duration':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'in miliseconds'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class ThermostatUIForm(UIBaseForm):
    class Meta:
        model = ThermostatUI
        child_fields = deepcopy(UIBaseForm.Meta.fields)
        child_fields.insert(4, 'power_status_function')
        child_fields.insert(5, 'current_temp_function')
        child_fields.insert(6, 'target_temp_function')
        child_fields.insert(7, 'speed_function')
        child_fields.insert(8, 'control_mode_function')
        child_fields.insert(9, 'operation_mode_function')
        child_fields.remove('on_color')
        child_fields.remove('off_color')
        fields = child_fields

    def __init__(self, *args, **kwargs):
        home_uuid = kwargs.get('home_uuid', None)
        project_uuid = kwargs.get('project_uuid', None)

        super(ThermostatUIForm, self).__init__(*args, **kwargs)

        if home_uuid and project_uuid:
            self.fields['power_status_function'].queryset = ThermostatDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()
            self.fields['current_temp_function'].queryset = ThermostatDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()
            self.fields['target_temp_function'].queryset = ThermostatDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()
            self.fields['speed_function'].queryset = ThermostatDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()
            self.fields['control_mode_function'].queryset = ThermostatDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()
            self.fields['operation_mode_function'].queryset = ThermostatDataPointFunction.objects.filter(
                device_base__parent_home__uuid=home_uuid,
                device_base__parent_project__uuid=project_uuid).all()

        for field_name, field in self.fields.items():
            if field_name == 'add_to_home':
                field.widget.attrs.update({"class": "form-check-input", "type": "checkbox"})
            elif field_name == 'off_color':
                field.widget.attrs.update(
                    {'id': 'colorpicker-off-color', 'class': 'form-control coloris instance1', 'value': '#45aaf2'})
            elif field_name == 'on_color':
                field.widget.attrs.update(
                    {'id': 'colorpicker-on-color', 'class': 'form-control coloris instance2', 'value': '#45aaf2'})
            elif field_name == 'on_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            elif field_name == 'off_icon':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'please select an icon then paste here'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

# it's good to define this function but for now it make my forms file messy, so we add it for next time :)
# class BaseFourPoleSwitchFormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         if any(self.errors):
#             return
#         if len(self.forms) != 4:
#             raise forms.ValidationError("Exactly four settings are required.")


fourPoleSwitch_dataPointFunction_formSet = inlineformset_factory(FourPoleSwitch, SwitchDataPointFunction,
                                                                 formset=BaseInlineFormSet,
                                                                 form=SwitchFunctionForm,
                                                                 extra=4,
                                                                 max_num=4,
                                                                 can_delete=False)

# fourPoleSwitch_dataPointFunction_formSet()
# fff = formset_factory(FourPoleSwitchForm)
# f = formset_factory(SwitchFunctionForm)
# fff()
# b= modelformset_factory()
# b()
# a = inlineformset_factory(FourPoleSwitch,SwitchDataPointFunction)
# a()


fivePoleSwitch_dataPointFunction_formSet = inlineformset_factory(FivePoleSwitch, SwitchDataPointFunction,
                                                                 formset=BaseInlineFormSet,
                                                                 form=SwitchFunctionForm,
                                                                 extra=5,
                                                                 max_num=5,
                                                                 can_delete=False)

thermostat_dataPointFunction_formSet = inlineformset_factory(Thermostat, ThermostatDataPointFunction,
                                                             formset=BaseInlineFormSet,
                                                             form=ThermostatFunctionForm,
                                                             extra=6,
                                                             max_num=6,
                                                             can_delete=False)

# switches_of_fourPoleThermostat_dataPointFunction_formSet = inlineformset_factory(FourPoleThermostat,
#                                                                                  SwitchDataPointFunction,
#                                                                                  formset=BaseInlineFormSet,
#                                                                                  fields=('display_name', 'function_name', 'switch_id'),
#                                                                                  extra=3, can_delete=False)

thermostat_of_fourPoleThermostat_dataPointFunction_formSet = inlineformset_factory(FourPoleThermostat,
                                                                                   ThermostatDataPointFunction,
                                                                                   formset=BaseInlineFormSet,
                                                                                   form=ThermostatFunctionForm,
                                                                                   extra=6,
                                                                                   max_num=6,
                                                                                   can_delete=False)

switches_of_tenPoleThermostat_dataPointFunction_formSet = inlineformset_factory(TenPoleThermostat,
                                                                                SwitchDataPointFunction,
                                                                                formset=BaseInlineFormSet,
                                                                                form=SwitchFunctionForm,
                                                                                extra=6,
                                                                                max_num=6,
                                                                                can_delete=False)

thermostat_of_tenPoleThermostat_dataPointFunction_formSet = inlineformset_factory(TenPoleThermostat,
                                                                                  ThermostatDataPointFunction,
                                                                                  formset=BaseInlineFormSet,
                                                                                  form=ThermostatFunctionForm,
                                                                                  extra=6,
                                                                                  max_num=6,
                                                                                  can_delete=False)


four_pole_switch_data_point_function_formset_initial = [
    {
        "display_name": "Switch 1",
        "function_name": "switch_1",
        "switch_id": 1,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 2",
        "function_name": "switch_2",
        "switch_id": 2,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 6",
        "function_name": "switch_6",
        "switch_id": 6,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 7",
        "function_name": "switch_7",
        "switch_id": 7,
        "value_type": 'BOOLEAN'
    }
]

five_pole_switch_data_point_function_formset_initial = [
    {
        "display_name": "Switch 1",
        "function_name": "switch_1",
        "switch_id": 1,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 2",
        "function_name": "switch_2",
        "switch_id": 2,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 4",
        "function_name": "switch_4",
        "switch_id": 4,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 6",
        "function_name": "switch_6",
        "switch_id": 6,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 7",
        "function_name": "switch_7",
        "switch_id": 7,
        "value_type": 'BOOLEAN'
    }
]

switches_of_ten_pole_thermostat_data_point_function_formset_initial = [
    {
        "display_name": "Switch 5",
        "function_name": "switch_5",
        "switch_id": 5,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 6",
        "function_name": "switch_6",
        "switch_id": 6,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 7",
        "function_name": "switch_7",
        "switch_id": 7,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 8",
        "function_name": "switch_8",
        "switch_id": 8,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 9",
        "function_name": "switch_9",
        "switch_id": 9,
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "Switch 10",
        "function_name": "switch_10",
        "switch_id": 10,
        "value_type": 'BOOLEAN'
    }
]

thermostat_data_point_formset_initial = [
    {
        "display_name": "power status",
        "function_name": "status",
        "value_type": 'BOOLEAN'
    },
    {
        "display_name": "current temperature",
        "function_name": "tmp",
        "value_type": 'DECIMAL'
    },
    {
        "display_name": "target temperature",
        "function_name": "spt",
        "value_type": 'DECIMAL'
    },
    {
        "display_name": "speed",
        "function_name": "fms",
        "value_type": 'STRING'
    },
    {
        "display_name": "control mode",
        "function_name": "fct",
        "value_type": 'STRING'
    },
    {
        "display_name": "operation mode",
        "function_name": "hc",
        "value_type": 'STRING'
    },
]







# from django import forms
# from django.forms import BaseInlineFormSet, inlineformset_factory
# from .models import FourPoleSwitch, SwitchSetting
#
#
# class FourPoleSwitchForm(forms.ModelForm):
#     class Meta:
#         model = FourPoleSwitch
#         fields = ['name']
#
#
# class BaseSwitchSettingFormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         if any(self.errors):
#             return
#         if len(self.forms) != 4:
#             raise forms.ValidationError("Exactly four settings are required.")
#
#
# SwitchSettingFormSet = inlineformset_factory(FourPoleSwitch, SwitchSetting, formset=BaseSwitchSettingFormSet, fields=('name', 'value'), extra=4, can_delete=False)









from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Use CustomUser if you have a custom user model
        fields = ('username', 'password1', 'password2', 'email')

class UserPermissionsForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = User  # Use CustomUser if you have a custom user model
        fields = ['permissions']
