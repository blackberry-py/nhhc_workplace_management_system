"""
Module: authentication.views
Description: This module contains a custom login view that extends the LoginView from allauth.account.views. It provides a custom implementation for determining the success URL after a user logs in.
Dependencies: allauth, compliance
""",
from allauth.account.views import LoginView, get_next_redirect_url, password_change
from authentication.models import UserProfile
from employee.models import Employee
from django.urls import resolve
from loguru import logger
from arrow import arrow
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

class CustomLoginView(LoginView):
    def get_success_url(self):
        # Assoicating the Login Attempt to a Possible User 
        if (re.fullmatch(regex, self.request.POST.get("login"))):
            user_attempting_to_login = Employee.objects.get(email=self.request.POST.get("login"))
        else: 
            user_attempting_to_login = Employee.objects.get(username=self.request.POST.get("login"))
        logger.debug(user_attempting_to_login)
        try:
        # If the user is logging in for the first time, redirect to the change password page
            user_profile = UserProfile.objects.get(user=user_attempting_to_login)
            logger.debug(user_attempting_to_login.last_login)
            if user_attempting_to_login.last_login is None:
                logger.debug('First Time Login Detected - Redirecting to Change ')
                return resolve('password/change/', {"first_login": True})
            elif arrow.get(user_profile.last_password_change).shift(months=+3)  >= arrow.now():
                logger.debug('90+ Day Password Detected - Redirecting to Change')
                return resolve('password/change/', {"90_day_change": True})
            else:
                return super().success_url
        except Exception as e: 
            logger.trace(f'Unable to Verify User Profile: {e}')            