from datetime import datetime

from authentication.models import UserProfile
from compliance.models import Compliance, Contract
from django.contrib import admin
from employee.models import Employee
from portal.models import PayrollException  # Assessment, InServiceTraining,
from web.models import ClientInterestSubmission, EmploymentApplicationModel

now = datetime.now()
# Register your models here.
all_models = [
    Contract,
    PayrollException,
    ClientInterestSubmission,
    EmploymentApplicationModel,
    UserProfile,
]


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
    change_form_template = "progressbarupload/change_form.html"
    add_form_template = "progressbarupload/change_form.html"


class ComplianceAdmin(admin.ModelAdmin):
    change_form_template = "progressbarupload/change_form.html"
    add_form_template = "progressbarupload/change_form.html"


admin.site.register(Compliance, ComplianceAdmin)
admin.site.register(Employee, EmployeeAdmin)
