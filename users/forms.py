from django import forms
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100,required=False)
    email = forms.EmailField()
    password = forms.CharField(max_length=100,widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=100,widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password',None)
        confirm_password = cleaned_data.get('confirm_password',None)

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password','Password and Confirm Password must match!')

        return cleaned_data