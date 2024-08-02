"""
Module: urls.py
Description: This module contains the URL patterns for the frontend application.
"""

from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from web import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="homepage"),
    path("about/", views.AboutUsView.as_view(), name="about"),
    path("client-interest/", views.ClientInterestFormView.as_view(), name="client_interest"),
    path("employment-application/", csrf_exempt(views.EmploymentApplicationFormView.as_view()), name="application"),
    path("submission-confirmation/", views.SuccessfulSubmission.as_view(), name="submitted"),
    re_path(r"^favicon.ico\/?/$", views.favicon, name="favicon"),
]
