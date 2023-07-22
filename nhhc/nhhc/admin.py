from compliance.models import Compliance
from compliance.models import Contract
from django.contrib import admin
from employee.models import Employee
from portal.models import Exception  # Assessment, InServiceTraining,
from django.contrib import admin
from web.models import ClientInterestSubmissions
from web.models import EmploymentApplicationModel

# Register your models here.
all_models = [
    Employee,
    Contract,
    Exception,
    Compliance,
    ClientInterestSubmissions,
    EmploymentApplicationModel,
]

for model in all_models:
    register = admin.site.register(model)
