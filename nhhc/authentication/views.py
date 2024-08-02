"""
Module: authentication.views
Description: This module contains a custom login view that extends the LoginView from allauth.account.views. It provides a custom implementation for determining the success URL after a user logs in.
Dependencies: allauth, compliance
""",
import re

from allauth.account.views import LoginView, get_next_redirect_url, password_change
from arrow import arrow
from authentication.forms import NHHCLoginForm
from authentication.models import UserProfile
from django.urls import resolve
from employee.models import Employee
from loguru import logger

regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


class CustomLoginView(LoginView):
    def get_form_class(self):
        super().get_form_class()
        return NHHCLoginForm()
