from django import forms
from django.contrib.auth.models import User
from dashboard.models import HomeUser



class EditProfileBaseUserForm(forms.ModelForm):
    current_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Current Password"
    }), label='Current Password', required=False)
    new_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "New Password"
    }), label="New Password", required=False)
    confirm_new_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Confirm New Password"
    }), label="Confirm New Password", required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super(EditProfileBaseUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if current_password:
            if not self.instance.check_password(current_password):
                self.add_error('current_password', "Current password is incorrect")

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', "New passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user


class EditProfileHomeUserForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file d-none'}), required=False)
    class Meta:
        model = HomeUser
        fields = ['avatar']
    
    def __init__(self, *args, **kwargs):
        super(EditProfileHomeUserForm, self).__init__(*args, **kwargs)



