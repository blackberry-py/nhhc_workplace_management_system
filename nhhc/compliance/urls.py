from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("all-employees/", views.employee_report_export, name="employee-export"),
]
