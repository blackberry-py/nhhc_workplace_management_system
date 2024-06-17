"""
This module contains views related to contract creation, compliance profiles, and attestation forms.

The module includes class-based views for creating contract forms, updating compliance profiles, and handling signed attestation forms. It also provides views for displaying and signing compliance documents using Docuseal.

Classes:
- CreateContractFormView: A view for creating a new contract form.
- ComplianceProfileDetailView: A DetailView for displaying Compliance object details.
- ComplianceProfileFormView: A view for updating compliance profiles.
- DocusealCompliaceDocsSigning_*: Views for displaying and signing compliance documents using Docuseal.

Functions:
- signed_attestations: Handles signed attestation forms.

Attributes:
- Various template names and context object names are defined for different views.

Note: The module structure is organized into sections for Contract Related Views, Compliance Related Views, and Attestation Forms.

For more detailed information on each class and function, refer to the individual docstrings within the code.

"""


import json
import os
from typing import Any
import requests
import boto3
from botocore.exceptions import ClientError
from compliance.forms import ComplianceForm, ContractForm
from compliance.models import Compliance
from compliance.tasks import process_signed_form
from django.http import HttpRequest, HttpResponse
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from employee.models import Employee
from formset.upload import FileUploadMixin
from loguru import logger
from rest_framework import status
from django.urls import  reverse_lazy
from nhhc.utils.upload import S3HANDLER

# SECTION - Contract Related Viewws

class SuccessfulUpdate(TemplateView):
    template_name = "successful_update.html"
    extra_context = {"title": "Form Updated Successfully"}

class CreateContractFormView(CreateView):
    """
    class-based template rendering view for creating a new contract form.

    Attributes:
    - template_name: a string representing the template file to render the form
    - form_class: the form class to use for creating the contract form
    """

    template_name = "new_contract.html"
    form_class = ContractForm


# !SECTION
# SECTION - Compliance Related Views
class ComplianceProfileDetailView(DetailView):
    """
    This class is a DetailView that displays the details of a Compliance object.
    """

    model = Compliance
    template_name = "compliance_details.html"
    context_object_name = "employee"

    def get_object(self) -> Compliance:
        """
        This method retrieves the Compliance object for the current user.

        Returns:
        Compliance object: The Compliance object for the current user.
        """
        return Compliance.objects.get(employee=self.request.user)


class ComplianceProfileFormView(UpdateView, FileUploadMixin):
    """
    This class is a view for updating compliance profiles.

    Attributes:
    - form_class: The form class to be used for updating compliance profiles.
    - model: The model to be used for updating compliance profiles.
    - template_name: The template to be rendered for the compliance form.
    - context_object_name: The context object name to be used in the template.
    """

    form_class = ComplianceForm
    model = Compliance
    template_name = "compliance_forms.html"
    context_object_name = "employee"
    success_url = reverse_lazy("form-updated")


#!SECTION
# SECTION - Attestation Forms


@require_POST
def signed_attestations(request: HttpRequest) -> HttpResponse:
    """
    Process signed document requests and assign file paths to employee attestations.

    Args:
        request (HttpRequest): The HTTP request object containing the document payload.

    Returns:
        HttpResponse(status code: 201): A response indicating the status of the file path assignment process.

    Raises:
        HttpResponse(status_code: 422): If an invalid document type is encountered during processing.
    """
    logger.info('Signed Document Request Recieved From AWS')
    try:
        logger.debug(request.body)
        docuseal_payload = json.loads(request.body)
        employee_id = docuseal_payload['data']['external_id']
        document_type = docuseal_payload['data']['template']['name']
        uploading_employee = Employee.objects.get(employee_id=employee_id)
        doc_type_prefix = ""
        document_id = docuseal_payload['data']['template']['id']
        employee_upload_suffix = f"{uploading_employee.last_name.lower()}_{uploading_employee.first_name.lower()}.pdf"
# fmt: off

        match document_type:
            case "Nett Hands - Do Not Drive Agreement - 2024":
                doc_type_prefix = "do_not_drive_agreement_attestation"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.do_not_drive_agreement_attestation = filepath
                uploading_employee.save()
            case "State of Illinois - Department of Revenue - Withholding Worksheet (W4)":
                doc_type_prefix = "state_w4_attestation"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.state_w4_attestation = filepath
                uploading_employee.save()
            case "US Internal Revenue Services - Withholding Certificate (W4) - 2024":
                doc_type_prefix = "irs_w4_attestation"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.state_w4_attestation = filepath
                uploading_employee.save()
            case "US Department of Homeland Security - Employment Eligibility Verification (I-9)":
                doc_type_prefix = "dha_i9"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.dha_i9 = filepath
                uploading_employee.save()
            case "Nett Hands HCA Policy - 2024":
                doc_type_prefix = "hca_policy_attestation"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.hca_policy_attestation = filepath
                uploading_employee.save()
            case "Nett Hands & Illinois Department of Aging General Policies":
                doc_type_prefix = "idoa_agency_policies_attestation"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.idoa_agency_policies_attestation = filepath
                uploading_employee.save()
            case "Nett Hands Homehealth Care Aide (HCA)  Job Desc - 2024":
                doc_type_prefix = "job_duties_attestation"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.job_duties_attestation = filepath
                uploading_employee.save()
            case "IDPH - Health Care Worker Background Check Authorization":
                doc_type_prefix = "idph_background_check_authorization"
                filepath = os.path.join("attestations",doc_type_prefix,"_".join(doc_type_prefix,employee_upload_suffix) )
                uploading_employee.idph_background_check_authorization = filepath
                uploading_employee.save()
            case _:
                logger.error(f'Invaild Document Type: {document_type} - {document_id}')
                return HttpResponse(content='Invaild Document Type', status=status.HTTP_406_NOT_ACCEPTABLE)
    # fmt: on

        if S3HANDLER.download_pdf_file(docuseal_payload):
            return HttpResponse(content="Processed File Path", status=status.HTTP_201_CREATED)
        else:
            return HttpResponse(content="Failed to Process File", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        logger.error(f'Unable to Assign FilePath: {e}')
        return HttpResponse(content="Unable to Assign FilePath", status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class DocusealCompliaceDocsSigning_IDOA(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/r5UbQeVsQgkwUp"
        context['title'] = "Nett Hands & Illinois Department of Aging General Policies"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_IDOA, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response



class DocusealCompliaceDocsSigning_HCA(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/3KA4PP4CEjpy4r"
        context['title'] = "US Department of Homeland Security - Employment Eligibility Verification"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_HCA, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response

class DocusealCompliaceDocsSigning_DoNotDrive(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/v1FPgz9xgBJVgH"
        context['title'] = "Nett Hands - Do Not Drive Agreement"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_DoNotDrive, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response


class DocusealCompliaceDocsSigning_JobDesc(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/KQUEkomQZr1ddD"
        context['title'] = "Nett Hands Homehealth Care Aide (HCA) Job Desc"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_JobDesc, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response

class DocusealCompliaceDocsSigning_i9(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/ovQk6ACHqajQvC"
        context['title'] = "US Department of Homeland Security - Employment Eligibility Verification"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_i9, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response

class DocusealCompliaceDocsSigning_irs_w4(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/wmJGUH3wU2GrUJ"
        context['title'] = "US Internal Revenue Services - Withholding Certificate"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_irs_w4, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response


class DocusealCompliaceDocsSigning_il_w4(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/M6o9cZ4528yk4L"
        context['title'] = "State of Illinois - Department of Revenue - Withholding Worksheet"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_il_w4, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response

class DocusealCompliaceDocsSigning_idph_bg_auth(TemplateView):
    """
    A view for displaying and signing compliance documents using Docuseal.

    Attributes:
    - template_name (str): The name of the template to be rendered.

    Methods:
    - get_context_data(self, **kwargs: Any) -> dict[str, Any]: Retrieves the context data for the view.
    """

    template_name = "docuseal.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["employee"] = Employee.objects.get(employee_id=self.request.user.employee_id)
        context["doc_url"] = "https://docuseal.co/d/RiVYseBYUpvrxD"
        context['title'] = "Health Care Worker Background Check Authorization"
        return context
    def dispatch(self, *args, **kwargs):
            response = super(DocusealCompliaceDocsSigning_idph_bg_auth, self).dispatch(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = "*"
            return response


# !SECTION
