"""
Copyright (c) 2019 - present AppSeed.us
"""
from allauth.account.views import LoginView, SignupView
from authentication.forms import EmployeeLoginForm
from compliance.models import Compliance

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.db.models import signals
from django.shortcuts import redirect, render, reverse
