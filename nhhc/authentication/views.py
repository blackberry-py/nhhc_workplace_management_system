"""
Module: authentication.views
Description: This module contains a custom login view that extends the LoginView from allauth.account.views. It provides a custom implementation for determining the success URL after a user logs in.
Dependencies: allauth, compliance
""",
from allauth.account.views import LoginView, get_next_redirect_url, password_change
from authentication.models import UserProfile
from employee.models import Employee
from authentication.forms import NHHCLoginForm
from django.urls import resolve
from loguru import logger
from arrow import arrow
import re

regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


class CustomLoginView(LoginView):
    def get_form_class(self):
        super().get_form_class()
        return NHHCLoginForm()
