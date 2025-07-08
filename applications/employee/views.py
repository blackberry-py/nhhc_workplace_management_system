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

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from loguru import logger
from rest_framework import status

from applications.compliance.models import Compliance
from applications.employee.models import Employee
from applications.employee.tasks import send_async_onboarding_email
from applications.web.models import EmploymentApplicationModel
from common.helpers import (
    get_content_for_unauthorized_or_forbidden,
    get_status_code_for_unauthorized_or_forbidden,
)
from common.mailer import PostOffice

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
class Hire:
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

    @staticmethod
    @require_POST
    @login_required
    @user_passes_test(lambda user: user.is_superuser)
    def hire(request: HttpRequest) -> HttpResponse:
        try:
            pk = Hire.parse_pk_from_request(request)
            applicant = Hire.get_applicant(pk)
            hired_user = Hire.process_hiring(applicant, request.user)
            Hire.send_hiring_notification(hired_user)
            content = Hire.prepare_success_content(hired_user)
            return HttpResponse(status=201, content=content)
        except ValueError:
            return Hire.invalid_pk_response()
        except EmploymentApplicationModel.DoesNotExist:
            return Hire.applicant_not_found_response()
        except Exception as e:
            return Hire.handle_general_exception(e)

    # Helper functions
    @staticmethod
    def parse_pk_from_request(request: HttpRequest) -> int:
        if pk := int(request.POST.get("pk")):
            return pk
        else:
            raise ValueError("Missing or invalid PK.")

    @staticmethod
    def get_applicant(pk: int) -> EmploymentApplicationModel:
        return EmploymentApplicationModel.objects.get(pk=pk)

    @staticmethod
    def process_hiring(applicant: EmploymentApplicationModel, user: Employee):
        applicant.hire_applicant(hired_by=user)
        applicant.save()
        return applicant

    @staticmethod
    def send_hiring_notification(hired_user) -> None:
        credentials = {
            "new_user_email": hired_user["email"],
            "new_user_first_name": hired_user["first_name"],
            "plaintext_temp_password": hired_user["plain_text_password"],
            "username": hired_user["username"],
        }
        notice = send_async_onboarding_email.delay(credentials)
        if not notice:
            logger.error(f"Email not sent: {notice}")

    @staticmethod
    def prepare_success_content(hired_user):
        return f"username: {hired_user['username']}, password: {hired_user['plain_text_password']}, employee_id: {hired_user['employee_id']}"

    @staticmethod
    def invalid_pk_response():
        logger.warning("Invalid or missing application PK submitted.")
        return HttpResponse(status=400, content="Failed to hire applicant. Invalid or no 'pk' value provided.")

    @staticmethod
    def applicant_not_found_response():
        logger.error("Employment application not found.")
        return HttpResponse(status=404, content="Failed to hire applicant. Employment application not found.")

    @staticmethod
    def handle_general_exception(e):
        logger.exception(f"Failed to hire applicant or send new user credentials. Error: {e}")
        return HttpResponse(
            status=422 if "hire_applicant" in str(e) else 424,
            content=f"Failed to hire applicant or send new user credentials. Error: {e}.",
        )


@require_POST
def promote(request: HttpRequest) -> HttpResponse:
    """
    This function is used to promote an applicant based on the provided 'pk' value in the request.

    Args:
        request (HttpRequest): The HTTP request object containing the 'pk' value.

    Returns:
        HttpResponse: Returns an HTTP response with a status code indicating the success or failure of the hiring process.

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
    This function is used to demote an employee based on the provided 'pk' value in the request.

    Args:
        request (HttpRequest): The HTTP request object containing the 'pk' value.

    Returns:
        HttpResponse: Returns an HTTP response with a status code indicating the success or failure of the demotion process.

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
