"""
Module: urls.py
Description: This module contains the URL patterns for the frontend application.
"""

from django.urls import path, re_path
from django.views.decorators.csrf import csrf_protect
from web import views

app_name = "web"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("about/", views.AboutUsView.as_view(), name="about_us"),
    path("client-interest/", views.ClientInterestFormView.as_view(), name="client_interest_form"),
    path("employment-application/", csrf_protect(views.EmploymentApplicationFormView.as_view()), name="employment_application_form"),
    path("submission-confirmation/", views.SuccessfulSubmission.as_view(), name="form_submission_success"),
]
