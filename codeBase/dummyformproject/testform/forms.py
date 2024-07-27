from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from .models import FourPoleSwitch, SwitchSetting


class FourPoleSwitchForm(forms.ModelForm):
    class Meta:
        model = FourPoleSwitch
        fields = ['name']



class BaseSwitchSettingFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if len(self.forms) != 4:
            raise forms.ValidationError("Exactly four settings are required.")


SwitchSettingFormSet = inlineformset_factory(FourPoleSwitch, SwitchSetting, formset=BaseSwitchSettingFormSet, fields=('name', 'value'), extra=4, can_delete=False)
