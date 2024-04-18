import os
from typing import Any

from compliance.forms import ComplianceForm, ContractForm
from compliance.models import Compliance
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from formset.upload import FileUploadMixin
from django.forms.models import model_to_dict
from employee.models import Employee

# Create your views here.


def create_contract(request):
    pass


class CreateContractFormView(FormView):
    template_name = "new_contract.html"
    form_class = ContractForm


class ComplianceProfileDetailView(DetailView):
    model = Compliance
    template_name = "compliance_details.html"
    context_object_name = "employee"

    def get_object(self):
        return Compliance.objects.get(employee=self.request.user)

    # def get_context_data(self, **kwargs) -> dict[str, Any]:
    #     context = super().get_context_data(**kwargs)
    #     initial = model_to_dict(self.get_object())
    #     context["form"] = ComplianceForm(initial=initial)
    #     return context


class ComplianceProfileFormView(UpdateView, FileUploadMixin):
    form_class = ComplianceForm
    model = Compliance
    template_name = "compliance_forms.html"
    context_object_name = "employee"

    # def get_slug_field(self):
    #     return self.employee_id

    # def get_object(self, pk):
    #     employee = Employee.objects.get(employee_id=pk)
    #     return Compliance.objects.get(employee = employee)

    # def get_success_url(self):
    #     return reverse("compliance-profile")


class ComplianceProfile(View):
    def get(self, request, *args, **kwargs):
        view = ComplianceProfileDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ComplianceProfileFormView.as_view()
        return view(request, *args, **kwargs)


def generate_report(requst):
    sessionDataCSV = f"TTPUpload{now.to_date_string()}.csv"
    sessions = employee_report_export()
    with open(sessionDataCSV, "w+") as csv_output_file_pointer:
        csv_writer = csv.writer(csv_output_file_pointer)
        # Writing headers of CSV file
        header = (
            "SSN",
            "FirstName",
            "LastName",
            "MiddleName",
            "DateOfBirth",
            "Gender",
            "EmailAddress",
            "Ethnicity",
            "Race",
            "Qualifications",
            "LanguageCode",
            "ContractNumber",
            "EmployeeTitle",
            "TitleStartDate",
            "CaseLoad",
            "Prior to 10/01/2021",
            "TrainingDate",
            "InitialCBC",
            "MostCurrentCBC",
        )
        csv_writer.writerow(header)
        for employee in employees:
            row_data = (
                employee["social_security"],
                employee["first_name"],
                employee["last_name"],
                employee["middle_name"],
                employee["date_of_birth"],
                employee["gender"],
                employee["ethnicity"],
                employee["race"],
                employee["qualifications"],
                employee["language"],
                employee["contract"],
                employee["title"],
                employee["hire_date"],
                "Find Out What Caseload Is" "False",
                " ",
                employee["initial_idph_background_check_completion_date"],
                employee["current_idph_background_check_completion_date"],
            )
            csv_writer.writerow(row_data)
            os.open(sessionDataCSV, os.O_NONBLOCK)
