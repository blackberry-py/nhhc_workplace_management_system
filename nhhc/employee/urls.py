from django.urls import path
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("employee/<int:pk>/", views.employee_details, name="employee"),
    path("rejected", csrf_exempt(views.reject), name="reject-application"),
    path("roster/", views.employee_roster, name="roster"),
]
