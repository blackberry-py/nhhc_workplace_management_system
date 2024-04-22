"""
Module: portal.urls
This module contains the URL patterns for the portal application.

The urlpatterns list contains the URL patterns for the views in the application. Each URL pattern is mapped to a specific view function and has a unique name for easy reference. Imported via includes in project root conf

Attributes:
    urlpatterns (list): A list of URL patterns mapped to view functions.

"""

from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from portal import views

urlpatterns = [
    path("dashboard", views.portal_dashboard, name="dashboard"),
    re_path(r"^profile/$", views.Profile.as_view(), name="profile"),
    path(
        "inquiries/",
        login_required(views.ClientInquiriesListView.as_view()),
        name="inquiries",
    ),
    path(
        "inquiries/<int:pk>/",
        login_required(views.ClientInquiriesDetailView.as_view()),
        name="client_interest_details",
    ),
    path(
        "reviewed",
        csrf_exempt(views.marked_reviewed),
        name="marked_reviewed",
    ),
    path(
        "api/inquiries",
        csrf_exempt(views.ClientInquiriesAPIListView.as_view()),
        name="all_client_inquiries_api",
    ),
    path(
        "applicants/",
        login_required(views.EmploymentApplicationListView.as_view()),
        name="applicants-list",
    ),
    path(
        "api/applicants",
        login_required(views.EmploymentApplicationModelAPIListView.as_view()),
        name="applicants_api",
    ),
    path(
        "applicant/<int:pk>",
        login_required(views.EmploymentApplicationDetailView.as_view()),
        name="applicant-details",
    ),
    path("all_applicants", views.all_applicants, name="submitted-applicants-api"),
    path("coming-soon/", views.coming_soon, name="coming-soon"),
]
