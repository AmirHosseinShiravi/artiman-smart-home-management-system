from django.shortcuts import render, get_object_or_404, redirect
from .models import FourPoleSwitch, SwitchSetting
from .forms import FourPoleSwitchForm, SwitchSettingFormSet


def create_four_pole_switch(request):
    if request.method == 'POST':
        form = FourPoleSwitchForm(request.POST)
        formset = SwitchSettingFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            four_pole_switch = form.save()
            formset.instance = four_pole_switch
            formset.save()
            return redirect('home')  # redirect to the appropriate page after saving
    else:
        form = FourPoleSwitchForm()
        formset = SwitchSettingFormSet()

    return render(request, 'edit_four_pole_switch.html', {'form': form, 'formset': formset, 'device': None})


def edit_four_pole_switch(request, device_id):
    device = get_object_or_404(FourPoleSwitch, id=device_id)
    if request.method == 'POST':
        form = FourPoleSwitchForm(request.POST, instance=device)
        formset = SwitchSettingFormSet(request.POST, instance=device)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('home')  # redirect to the appropriate page after saving
    else:
        form = FourPoleSwitchForm(instance=device)
        formset = SwitchSettingFormSet(instance=device)

    return render(request, 'edit_four_pole_switch.html', {'form': form, 'formset': formset, 'device': device})
