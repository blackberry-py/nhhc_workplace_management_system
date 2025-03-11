"""
Modeule: employee.urls
This module contains the URL patterns for the employee management application.


The URL patterns include:
- employee_details: Retrieves details of a specific employee
- reject-application: Allows for the rejection of an application with CSRF exemption
- employee_roster: Displays the roster of employees
- hire-employee: Handles the hiring of new employees

These URL patterns are used to define the routing for the views in the application.

"""

from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

from applications.employee import views
from applications.employee.api import endpoints

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"employees", endpoints.EmployeeViewSet)

app_name = "employee"
urlpatterns = [
    path(
        "employee/<int:pk>/",
        login_required(views.EmployeeDetail.as_view()),
        name="employee",
    ),
    path("applicant/reject/", csrf_exempt(views.reject), name="reject"),
    path("roster/", login_required(views.EmployeeRoster.as_view()), name="roster"),
    path("applicant/hire/", views.Hire.hire, name="hire"),
    # re_path(r"^accounts/login/$", views.force_pwd_login),
    path("employee/promote/", csrf_exempt(views.promote), name="promote_employee"),
    path("employee/demote/", csrf_exempt(views.demote), name="promote_employee"),
    path("api", include(router.urls)),
]
