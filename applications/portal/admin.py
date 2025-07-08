from datetime import datetime

from django.contrib import admin

from applications.announcements.models import Announcements
from applications.authentication.models import UserProfile
from applications.compliance.models import Compliance, Contract
from applications.employee.models import Employee
from applications.portal.models import (
    PayrollException,  # Assessment, InServiceTraining,
)
from applications.web.models import ClientInterestSubmission, EmploymentApplicationModel

now = datetime.now()
# Register your models here.
all_models = [Contract, PayrollException, Announcements, ClientInterestSubmission, EmploymentApplicationModel, UserProfile, Compliance]


for model in all_models:
    admin.site.register(model)


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
    readonly_fields = ["employee_id"]


admin.site.register(Employee, EmployeeAdmin)
