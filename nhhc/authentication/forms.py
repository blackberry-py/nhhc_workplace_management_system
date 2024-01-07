# """
# Copyright (c) 2019 - present AppSeed.us
# """
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import get_user_model
# from allauth.account.authentication import record_authentication
# from django.utils.translation import gettext_lazy as _

# 


# class NHHCLoginForm(LoginForm):

#     def login(self, *args, **kwargs):
#         credentials = self.user_credentials()
#         extra_data = {
#             field: credentials.get(field)
#             for field in ["email", "username"]
#             if field in credentials
#         }
#         record_authentication(request, method="password", **extra_data)
#         ret = perform_login(
#             request,
#             self.user,
#             email_verification=app_settings.EMAIL_VERIFICATION,
#             redirect_url=redirect_url,
#             email=credentials.get("email"),
#         )
#         remember = app_settingsƒ.SESSION_REMEMBER
#         if remember is None:
#             remember = self.cleaned_data["remember"]
#         if remember:
#             request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
#         else:
#             request.session.set_expiry(0)
#         return super(NHHCLoginForm, self).login(*args, **kwargs)


# class SignUpForm(UserCreationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={"placeholder": "Username", "class": "form-control"},
#         ),
#     )
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={"placeholder": "Email", "class": "form-control"},
#         ),
#     )
#     password1 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={"placeholder": "Password", "class": "form-control"},
#         ),
#     )
#     password2 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={"placeholder": "Password check", "class": "form-control"},
#         ),
#     )

#     class Meta:
#         model = get_user_model()
#         fields = ("username", "email", "password1", "password2")


"""
Copyright (c) 2019 - present AppSeed.us
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from allauth.account.authentication import record_authentication
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from allauth.account.forms import LoginForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Employee First Name", "class": "form-control"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Employee Last Name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"placeholder": "Confirm Password", "class": "form-control"}),
        }


class EmployeeLoginForm(LoginForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username or Email", "class": "form-control"},
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter Me", "class": "form-control"},
        ),
    )
    remember = forms.BooleanField(label=_("Remember Me"), required=False)

    def login(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        remember = self.cleaned_data.get("remember")

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return super(EmployeeLoginForm, self).login(request, redirect_url=reverse('dashboard'))
            else:
                return forms.ValidationError("This account is currently inactive.")
        else:
            return forms.ValidationError("Invalid login credentials provided.")