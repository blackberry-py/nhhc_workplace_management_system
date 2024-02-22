from authentication.models import UserProfile
from compliance.models import Compliance, Contract
from django.contrib import admin
from employee.models import Employee
from portal.models import Exception  # Assessment, InServiceTraining,
from web.models import ClientInterestSubmissions, EmploymentApplicationModel

# Register your models here.
all_models = [
    Contract,
    Exception,
    Compliance,
    ClientInterestSubmissions,
    EmploymentApplicationModel,
    UserProfile,
]


class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ["username", "first_name", "last_name", "social_security", "phone"]
    list_display = ["first_name", "last_name", "username", "hire_date"]


for model in all_models:
    admin.site.register(model)

admin.site.register(Employee, EmployeeAdmin)
