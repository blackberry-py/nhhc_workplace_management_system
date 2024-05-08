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
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from employee import views
from employee.models import Employee
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


# ViewSets define the view behavior.
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"employees", EmployeeViewSet)

urlpatterns = [
    path(
        "employee/<int:pk>/",
        login_required(views.EmployeeDetail.as_view()),
        name="employee",
    ),
    path("applicant/reject/", csrf_exempt(views.reject), name="reject-application"),
    path("roster/", login_required(views.EmployeeRoster.as_view()), name="roster"),
    path("applicant/hire/", csrf_exempt(views.hire), name="hire-employee"),
    # re_path(r"^accounts/login/$", views.force_pwd_login),
    path("employee/terminate/", csrf_exempt(views.terminate), name="terminate_employee"),
    path("api", include(router.urls)),
]
