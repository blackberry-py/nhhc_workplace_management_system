"""
Module: authentication.views
Description: This module contains a custom login view that extends the LoginView from allauth.account.views. It provides a custom implementation for determining the success URL after a user logs in.
Dependencies: allauth, compliance
"""
from allauth.account.views import LoginView, SignupView, get_next_redirect_url
from authentication.models import UserProfile
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.db.models import signals
from django.shortcuts import redirect, render, reverse
from loguru import logger

class CustomLoginView(LoginView):
    def get_success_url(self):
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            if user_profile.force_password_change: 
                return reverse('account_change_password')
            else:
                return super().get_success_url()
        except Exception as e: 
            logger.trace(f'Unable to Verify User Profile: {e}')