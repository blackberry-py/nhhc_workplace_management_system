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
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from employee import views

urlpatterns = [
    path("employee/<int:pk>/", views.employee_details, name="employee"),
    path("rejected", csrf_exempt(views.reject), name="reject-application"),
    path("roster/", views.employee_roster, name="roster"),
    path("hired/", csrf_exempt(views.hire), name="hire-employee"),
]
