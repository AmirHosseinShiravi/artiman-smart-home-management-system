from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import DeviceBase, DataPointFunction, SwitchDataPointFunction, ThermostatDataPointFunction,\
                    Switch, FourPoleSwitch, FivePoleSwitch, Thermostat, FourPoleThermostat, TenPoleThermostat,\
                    DeviceSwitchActions, SwitchUI, PushButtonUI, CurtainUI, ThermostatUI


class DeviceBaseForm(forms.ModelForm):
    class Meta:
        model = DeviceBase
        fields = ['name', 'uuid', 'descriptions']


class DataPointFunctionForm(forms.ModelForm):
    class Meta:
        model = DataPointFunction
        fields = ['display_name', 'function_name', 'value', 'value_type']


class SwitchFunctionForm(forms.ModelForm):
    class Meta:
        model = SwitchDataPointFunction
        fields = ['display_name', 'switch_id', 'function_name', 'value', 'value_type', 'function_type']
        # widgets = {
        #     'display_name': forms.TextInput(attrs={})
        # }


class ThermostatFunctionForm(forms.ModelForm):
    class Meta:
        model = ThermostatDataPointFunction
        fields = ['display_name', 'function_name', 'value', 'value_type', 'function_type']


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
                                                                 fields=('display_name', 'function_name', 'switch_id'),
                                                                 extra=3, can_delete=False)

thermostat_dataPointFunction_formSet = inlineformset_factory(Thermostat, ThermostatDataPointFunction,
                                                             formset=BaseInlineFormSet,
                                                             fields=('display_name', 'function_name'),
                                                             can_delete=False)


switches_of_fourPoleThermostat_dataPointFunction_formSet = inlineformset_factory(FourPoleThermostat, SwitchDataPointFunction,
                                                                                 formset=BaseInlineFormSet,
                                                                                 fields=('display_name', 'function_name', 'switch_id'),
                                                                                 extra=3, can_delete=False)

thermostat_fourPoleThermostat_dataPointFunction_formSet = inlineformset_factory(FourPoleThermostat, ThermostatDataPointFunction,
                                                                                formset=BaseInlineFormSet,
                                                                                fields=('display_name', 'function_name'),
                                                                                can_delete=False)

four_pole_switch_data_point_function_formset_initial = [
    {
        "display_name": "Switch 1",
        "function_name": "switch_1",
        "switch_id": 1
    },
    {
        "display_name": "Switch 2",
        "function_name": "switch_2",
        "switch_id": 2
    },
    {
        "display_name": "Switch 6",
        "function_name": "switch_6",
        "switch_id": 6
    },
    {
        "display_name": "Switch 7",
        "function_name": "switch_7",
        "switch_id": 7
    }
]

five_pole_switch_data_point_function_formset_initial = [
    {
        "display_name": "Switch 1",
        "function_name": "switch_1",
        "switch_id": 1
    },
    {
        "display_name": "Switch 2",
        "function_name": "switch_2",
        "switch_id": 2
    },
    {
        "display_name": "Switch 4",
        "function_name": "switch_4",
        "switch_id": 4
    },
    {
        "display_name": "Switch 6",
        "function_name": "switch_6",
        "switch_id": 6
    },
    {
        "display_name": "Switch 7",
        "function_name": "switch_7",
        "switch_id": 7
    }
]

thermostat_with_four_pole_switch_data_point_function_formset_initial = [
    {
        "display_name": "Switch 1",
        "function_name": "switch_1",
        "switch_id": 1
    },
    {
        "display_name": "Switch 2",
        "function_name": "switch_2",
        "switch_id": 2
    },
    {
        "display_name": "Switch 6",
        "function_name": "switch_6",
        "switch_id": 6
    },
    {
        "display_name": "Switch 7",
        "function_name": "switch_7",
        "switch_id": 7
    }
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