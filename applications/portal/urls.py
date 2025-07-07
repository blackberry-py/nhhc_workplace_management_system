"""
Module: portal.urls
This module contains the URL patterns for the portal application.

The urlpatterns list contains the URL patterns for the views in the application. Each URL pattern is mapped to a specific view function and has a unique name for easy reference. Imported via includes in project root conf

Attributes:
    urlpatterns (list): A list of URL patterns mapped to view functions.

"""

from django.contrib.auth.decorators import login_required
from django.urls import path, re_path

from applications.portal import views
from applications.portal.api import endpoints

app_name = "portal"
urlpatterns = [
    path("dashboard", views.Dashboard.as_view(), name="dashboard"),
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
        endpoints.marked_reviewed,
        name="marked_reviewed",
    ),
    path(
        "api/inquiries",
        endpoints.ClientInquiriesAPIListView.as_view(),
        name="all_client_inquiries_api",
    ),
    path(
        "applicants/",
        login_required(views.EmploymentApplicationListView.as_view()),
        name="applicants-list",
    ),
    path(
        "api/applicants",
        endpoints.EmploymentApplicationModelAPIListView.as_view(),
        name="applicants_api",
    ),
    path(
        "applicant/<int:pk>",
        login_required(views.EmploymentApplicationDetailView.as_view()),
        name="applicant-details",
    ),
    path("all_applicants", endpoints.all_applicants, name="submitted-applicants-api"),
    path("coming-soon/", views.coming_soon, name="coming-soon"),
    path("exceptions/", views.PayrollExceptionView.as_view(), name="exceptions"),
]
