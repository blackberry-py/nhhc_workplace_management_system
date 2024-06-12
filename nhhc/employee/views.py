"""
Module: employee.views


This module contains views and functions for managing employee information, including hiring, rejecting, and viewing employee details.

Functions:
- hire(request): Handles the hiring of applicants and sends new user credentials.
- reject(request): Handles the rejection of applicants.
- employee_roster(request): Renders the employee listing page.
- employee_details(request, pk): Renders the employee details page and allows for editing employee information.

Usage:
To use the functions in this module, import the module and call the desired function with the appropriate parameters.
"""


from typing import Any

from compliance.models import Compliance
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django_filters.rest_framework import DjangoFilterBackend
from employee.models import Employee
from employee.tasks import send_async_onboarding_email
from loguru import logger
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from web.models import EmploymentApplicationModel
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from nhhc.utils.helpers import (
    get_content_for_unauthorized_or_forbidden,
    get_status_code_for_unauthorized_or_forbidden,
)
from nhhc.utils.mailer import PostOffice

# from  employee.tasks import send_async_onboarding_email, send_async_rejection_email
# SECTION - Template - Rendering & API Class-Based Views
HR_MAILROOM = PostOffice("HR@netthandshome.care")


# SECTION - Templates
class EmployeeRoster(ListView):
    """
    A class-based template view that displays a list of employees in a paginated format.

    Attributes:
    - model: The model used for retrieving the list of employees.
    - queryset: The query set used to fetch all employees ordered by last name.
    - template_name: The HTML template used for rendering the employee listing.
    - context_object_name: The name used to refer to the list of employees in the template.
    - paginate_by: The number of employees to display per page.
    """

    model = Employee
    queryset = Employee.objects.all().order_by("last_name")
    template_name = "employee-listing.html"
    context_object_name = "employees"
    # paginate_by = 25


@method_decorator(never_cache, name="dispatch")
class EmployeeDetail(DetailView):
    """
    A class-based template view that displays detailed information about an employee.

    Inherits from Django's DetailView class.

    Attributes:
    - model: The model that this view will interact with (Employee).
    - template_name: The name of the template used to render the view ("employee-detail.html").
    - context_object_name: The name of the variable containing the object in the template ("employee").
    """

    model = Employee
    template_name = "employee-detail.html"
    context_object_name = "employee"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["compliance"] = Compliance.objects.get(employee=self.get_object())
        return context


# !SECTION

# SECTION - API Endpoints


class EmployeeRosterAPIView(ListCreateAPIView):
    """
    REST API endpoint for managing the list and creation of Employee objects.

    Attributes:
    queryset (QuerySet): A queryset of all Employee objects.
    serializer_class (tuple): A tuple containing the serializer class for Employee objects.
    permission_classes (list): A list of permission classes required for accessing this view.
    filter_backends (list): A list of filter backends used for filtering Employee objects.
    filterset_fields (list): A list of fields that can be used for filtering Employee objects.
    """

    queryset = Employee.objects.all()
    serializer_class = (EmploymentApplicationModel,)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "is_active",
        "is_superuser",
        "gender",
        "language",
        "marital_status",
        "ethnicity",
        "race",
        "city",
        "state",
        "ethnicity",
        "zipcode",
        "qualifications",
        "in_compliance",
        "onboarded",
    ]


# !SECTION

# !SECTION


# SECTION AJAX Hook Views


@require_POST
def reject(request: HttpRequest) -> HttpResponse:
    """
    Ajax Hook that updates EmploymentApplicationModel sets application status to REJECTED

    Args:
        request: HttpRequest  instance of the current request being processed

    Returns:
        HttpResponse - Returns status  code 204 if successful or a 418 and logs error message on failure
    """
    try:
        pk = request.POST.get("pk")
        submission = EmploymentApplicationModel.objects.get(id=pk)
        submission.reject_applicant(rejected_by=request.user)  # type: ignore
        HR_MAILROOM.send_external_applicant_rejection_email(submission)
        logger.success(f"Application Rejected for {submission.last_name}. {submission.first_name}")
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"JS AJAX Request Failed - Applicant Not Rejected = {e}")
        return HttpResponse(status=status.HTTP_406_NOT_ACCEPTABLE)


@require_POST
def hire(request: HttpRequest) -> HttpResponse:
    """
    Handle the process of hiring an applicant.

    This function takes a HttpRequest object as input and returns an HttpResponse object.
    It first checks if the user is authenticated and has superuser permissions. If not, it returns an unauthorized or forbidden response.

    Args:
        request (HttpRequest): The request object containing information about the user and the application.

    Returns:
        HttpResponse: The response object with the appropriate status code and content.
                400 - If POST body does not a vaild PK \n
                404 - If PK from POST body ids not matched to as vaild Employment Application \n
                422 - If Internal Conversion of Applicant to Employee Fails \n
                424 - If Creds Notification Email or Notice to the Front End Fails \n
                201 - On Successful hiring and notification\n
    Raises:
        ValueError: If the 'pk' value is invalid or not provided in the request.
        DoesNotExist: If the employment application with the provided 'pk' does not exist.
    """
    # Condition Checked: Requesting User is Logged in and An Admin
    if not request.user.is_authenticated or not request.user.is_superuser:
        logger.warning("No Authenticated or Non-Admin Hire Request Recieved - Denying Request")
        return HttpResponse(
            status=get_status_code_for_unauthorized_or_forbidden(request),
            content=get_content_for_unauthorized_or_forbidden(request),
        )
    # Condition Checked: POST REQUEST  is vaild with a interger PK in body in key `pk`
    try:
        pk = int(request.POST.get("pk"))  # type: ignore
        logger.debug(f"Hire Request Initated for Employee ID: {pk}")
    except (ValueError, TypeError):
        logger.warning("Bad Request to Hire Applicant, Invalid or NO Applcation PK Submitted")
        return HttpResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content=bytes(
                "Failed to hire applicant. Invalid or no 'pk' value provided in the request.",
                "utf-8",
            ),
        )

    # Condition Checked: Provided PK id associated with a vaild ID of an Submitted EmploymentApplicationModel
    try:
        applicant = EmploymentApplicationModel.objects.get(pk=pk)
        logger.debug(f"Hire Request Resolving to {applicant.last_name}, {applicant.first_name}")
    except EmploymentApplicationModel.DoesNotExist:
        logger.error("Failed to hire applicant. Employment application not found.")
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=bytes("Failed to hire applicant. Employment application not found.", "utf-8"),
        )
    # Condition Checked: An Corrosponding Employee Model Instance is created via the .hire_applicant method on the EmploymentApplicationModel class
    try:
        hired_user = applicant.hire_applicant(hired_by=request.user)  # type: ignore
        logger.debug(f"Created User Account. Returning: {hired_user}")
    except Exception as e:
        logger.error(f"Failed to hire applicant. Error: {e}")
        return HttpResponse(
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=bytes(f"Failed to hire applicant. Error: {e}.", "utf-8"),
        )
    # Condition Checked: New User Creds are Sent VIA email and Frontend has been provided confirmation
    try:
        applicant.save()
        new_user_credentials = {
            "new_user_email": hired_user["email"],
            "new_user_first_name": hired_user["first_name"],
            "plaintext_temp_password": hired_user["plain_text_password"],
            "username": hired_user["username"],
        }
        send_async_onboarding_email.delay(new_user_credentials)
        content = f"username: {hired_user['username']},  password: {hired_user['plain_text_password']}, employee_id: {hired_user['employee_id']}"
        logger.success(f"Successfully Converted Appicant to Employee - {hired_user['last_name']}, {hired_user['first_name']}")
        return HttpResponse(status=status.HTTP_201_CREATED, content=bytes(content, "utf-8"))
    except Exception as e:
        logger.exception(f"Failed to send new user credentials. Error: {e}")
        return HttpResponse(
            status=status.HTTP_424_FAILED_DEPENDENCY,
            content=bytes(f"Failed to send new user credentials. Error: {e}.", "utf-8"),
        )


@require_POST
def terminate(request: HttpRequest) -> HttpResponse:
    """
    This function is used to terminates an applicant based on the provided 'pk' value in the request.

    Args:
    - request (HttpRequest): The HTTP request object containing the 'pk' value.

    Returns:
    - HttpResponse: Returns an HTTP response with a status code indicating the success or failure of the hiring process.
    """
    # Condition Checked: Requesting User is Logged in and An Admin
    if not request.user.is_authenticated or not request.user.is_superuser:
        logger.warning("No Authenticated or Non-Admin Termination Request Recieved - Denying Request")
        return HttpResponse(
            status=get_status_code_for_unauthorized_or_forbidden(request),
            content=get_content_for_unauthorized_or_forbidden(request),
        )
    # Condition Checked: POST REQUEST  is vaild with a interger PK in body in key `pk`
    try:
        user = authenticate(username=request.user.username, password=request.POST.get("password"))
        if user is not None:
            pk = request.POST.get("pk")
            logger.debug(f"Termination Request Initated for Employee ID: {pk}")
        else:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN, content="Invaild Password User Combonataton")
    except (ValueError, TypeError):
        logger.info("Bad Request to Hire Applicant, Invaild or NO Applcation PK Submitted")
        return HttpResponse(
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content="Failed to terminate employee. Invalid or no 'pk' value provided in the request.",
        )
    # Condition Checked: Provided PK Employee ID associated with an Employee Instance
    try:
        terminated_employee = Employee.objects.get(id=pk)
        logger.debug(f"Termination Request Resolving to {terminated_employee.last_name}, {terminated_employee.first_name}")
    except Employee.DoesNotExist:
        logger.info("Failed to hire applicant. Employment application not found.")
        return HttpResponse(status=404, content="Failed to terminate employee.. Employee not found.")
    # Condition Checked: An Corrosponding Employee Model Instance is created via the .terminate_employment method on the Employee class
    try:
        terminated_employee.terminate_employment()
        logger.success(f"employment status for {terminated_employee.last_name}, {terminated_employee.first_name} TERMINATED")
        return HttpResponse(status=204)
    except Exception as e:
        logger.exception(f"Failed to terminate employee. Error: {e}.")
        return HttpResponse(status=400, content=f"Failed to terminate employee.. Error: {e}.")


@require_POST
def promote(request: HttpRequest) -> HttpResponse:
    """
    This function is used to promote an applicant based on the provided 'pk' value in the request.

    Args:
    - request (HttpRequest): The HTTP request object containing the 'pk' value.

    Returns:
    - HttpResponse: Returns an HTTP response with a status code indicating the success or failure of the hiring process.
    """
    # Check if the requesting user is logged in and an admin
    if not request.user.is_authenticated or not request.user.is_superuser:
        logger.warning("No Authenticated or Non-Admin Termination Request Received - Denying Request")
        return HttpResponse(
            status=get_status_code_for_unauthorized_or_forbidden(request),
            content=get_content_for_unauthorized_or_forbidden(request),
        )

    # Authenticate the user
    try:
        user = authenticate(username=request.user.username, password=request.POST.get("password"))
        if user is None:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN, content="Invalid Password User Combination")

        # Get the employee ID from the request
        pk = request.POST.get("pk")
        if not pk:
            logger.info("Bad Request to Promote Applicant, Invalid or No Application PK Submitted")
            return HttpResponse(
                status=status.HTTP_400_BAD_REQUEST,
                content="Failed to promote employee. Invalid or no 'pk' value provided in the request.",
            )

        # Get the employee instance from the provided PK
        try:
            promoted_employee = Employee.objects.get(employee_id=pk)
            logger.debug(f"Promotion Request Resolving to {promoted_employee.last_name}, {promoted_employee.first_name}")

            # Promote the employee to admin
            try:
                promoted_employee.promote_to_admin()
                logger.success(f"Employment status for {promoted_employee.last_name}, {promoted_employee.first_name} PROMOTED")
                return HttpResponse(status=204)
            except Exception as e:
                logger.exception(f"Failed to promote employee. Error: {e}")
                return HttpResponse(status=400, content=f"Failed to promote employee. Error: {e}")

        except Employee.DoesNotExist:
            logger.info("Failed to promote employee. Employee not found.")
            return HttpResponse(status=404, content="Failed to promote employee. Employee not found.")

    except (ValueError, TypeError):
        logger.info("Bad Request to Promote Applicant, Invalid or No Application PK Submitted")
        return HttpResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content="Failed to promote employee. Invalid or no 'pk' value provided in the request.",
        )

@require_POST
def demote(request: HttpRequest) -> HttpResponse:
    """
    This function is used to promote an applicant based on the provided 'pk' value in the request.

    Args:
    - request (HttpRequest): The HTTP request object containing the 'pk' value.

    Returns:
    - HttpResponse: Returns an HTTP response with a status code indicating the success or failure of the hiring process.
    """
    # Check if the requesting user is logged in and an admin
    if not request.user.is_authenticated or not request.user.is_superuser:
        logger.warning("No Authenticated or Non-Admin Termination Request Received - Denying Request")
        return HttpResponse(
            status=get_status_code_for_unauthorized_or_forbidden(request),
            content=get_content_for_unauthorized_or_forbidden(request),
        )

    # Authenticate the user
    try:
        user = authenticate(username=request.user.username, password=request.POST.get("password"))
        if user is None:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN, content="Invalid Password User Combination")

        # Get the employee ID from the request
        pk = request.POST.get("pk")
        if not pk:
            logger.info("Bad Request to Demote Applicant, Invalid or No Application PK Submitted")
            return HttpResponse(
                status=status.HTTP_400_BAD_REQUEST,
                content="Failed to demote employee. Invalid or no 'pk' value provided in the request.",
            )

        # Get the employee instance from the provided PK
        try:
            demoted_employee = Employee.objects.get(employee_id=pk)
            logger.debug(f"Demotion Request Resolving to {demoted_employee.last_name}, {demoted_employee.first_name}")

            # Promote the employee to admin
            try:
                demoted_employee.demote_from_admin()
                logger.success(f"Employment status for {demoted_employee.last_name}, {demoted_employee.first_name} DEMOTED")
                return HttpResponse(status=204)
            except Exception as e:
                logger.exception(f"Failed to promote employee. Error: {e}")
                return HttpResponse(status=400, content=f"Failed to promote employee. Error: {e}")

        except Employee.DoesNotExist:
            logger.info("Failed to promote employee. Employee not found.")
            return HttpResponse(status=404, content="Failed to promote employee. Employee not found.")

    except (ValueError, TypeError):
        logger.info("Bad Request to Promote Applicant, Invalid or No Application PK Submitted")
        return HttpResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content="Failed to promote employee. Invalid or no 'pk' value provided in the request.",
        )