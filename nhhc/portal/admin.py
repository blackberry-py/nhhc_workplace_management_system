from datetime import datetime

from announcements.models import Announcements
from authentication.models import UserProfile
from compliance.models import Compliance, Contract
from django.contrib import admin
from employee.models import Employee
from portal.models import (  # Assessment, InServiceTraining,
    FeatureFlag,
    PayrollException,
)
from web.models import ClientInterestSubmission, EmploymentApplicationModel

now = datetime.now()
# Register your models here.
all_models = [Contract, PayrollException, Announcements, ClientInterestSubmission, EmploymentApplicationModel, UserProfile, Compliance]


for model in all_models:
    admin.site.register(model)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    This class represents the admin interface for managing employee data.

    Attributes:
    - search_fields (list): A list of fields that can be searched in the admin interface.
    - list_display (list): A list of fields to display in the admin interface.
    - actions (list): A list of actions that can be performed on selected employees.
    - date_hierarchy (str): The field used for date-based drilldown in the admin interface.
    """

    search_fields = ["username", "first_name", "last_name", "social_security", "phone"]
    list_display = ["first_name", "last_name", "username", "hire_date"]
    actions = []
    date_hierarchy = "hire_date"


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("name", "is_enabled", "modified")
    list_editable = ("is_enabled",)
    date_hierarchy = "modified"
