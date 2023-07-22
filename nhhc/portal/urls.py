from django.urls import path
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("dashboard", views.index, name="home"),
    path("my-profile/", views.profile, name="profile"),
    path("inquiries/", views.client_inquiries, name="inquiries"),
    path(
        "inquiries/<int:pk>/",
        views.submission_detail,
        name="client_interest_details",
    ),
    path(
        "reviewed",
        csrf_exempt(views.marked_reviewed),
        name="marked_reviewed",
    ),
    path(
        "all_client_inquiries/",
        csrf_exempt(views.all_client_inquiries),
        name="all_client_inquiries",
    ),
    path("applicants/", views.employment_applications, name="applicants-list"),
    path("applicant/<int:pk>", views.applicant_details, name="applicant-details"),
    path("all_applicants", views.all_applicants, name="submitted-applicants-api"),
]
