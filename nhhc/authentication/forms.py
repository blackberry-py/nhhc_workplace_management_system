"""
Copyright (c) 2019 - present AppSeed.us
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from allauth.account.authentication import record_authentication
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import LoginForm


class NHHCLoginForm(LoginForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"},
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter Me", "class": "form-control"},
        ),
    )
    remember = forms.BooleanField(label=_("Remember Me"), required=False)

    def login(self, *args, **kwargs):
        credentials = self.user_credentials()
        extra_data = {
            field: credentials.get(field)
            for field in ["email", "username"]
            if field in credentials
        }
        record_authentication(request, method="password", **extra_data)
        ret = perform_login(
            request,
            self.user,
            email_verification=app_settings.EMAIL_VERIFICATION,
            redirect_url=redirect_url,
            email=credentials.get("email"),
        )
        remember = app_settingsƒ.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data["remember"]
        if remember:
            request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
        else:
            request.session.set_expiry(0)
        return super(NHHCLoginForm, self).login(*args, **kwargs)


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"},
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"},
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"},
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password check", "class": "form-control"},
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")
