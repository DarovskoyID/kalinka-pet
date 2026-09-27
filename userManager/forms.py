from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput())
    agree = forms.BooleanField(widget=forms.CheckboxInput(), required=True)
    class Meta:
        model = get_user_model()
        fields = ['username',
                  'first_name',
                  'last_name',
                  'email',
                  'password',
                  'telegram_id']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают")
        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password", e)
        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        