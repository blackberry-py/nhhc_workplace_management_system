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


from compliance.models import Compliance
from django.conf import settings
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django_filters.rest_framework import DjangoFilterBackend
from employee.forms import EmployeeForm
from employee.models import Employee
from loguru import logger
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from web.models import EmploymentApplicationModel

from nhhc.utils import (
    get_content_for_unauthorized_or_forbidden,
    get_status_code_for_unauthorized_or_forbidden,
    send_new_user_credentials,
)

logger.add(
    settings.DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG"
)
logger.add(
    settings.PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO"
)
logger.add(
    settings.LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO"
)


# SECTION - Template - Rendering & API Class-Based Views


# SECTION - Templates
class EmployeeRoster(ListView):
    model = Employee
    queryset = Employee.objects.all().order_by("last_name")
    template_name = "employee-listing.html"
    context_object_name = "employees"
    paginate_by = 25


class EmployeeDetail(DetailView):
    model = Employee
    template_name = "employee-details.html"
    context_object_name = "employee"


# !SECTION

# SECTION - API Endpoints


class EmployeeRosterAPIView(ListCreateAPIView):
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
        submission.save()
        logger.success(
            f"Application Rejected for {submission.last_name}. {submission.first_name}"
        )
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"JS AJAX Request Failed - Applicant Not Rejected = {e}")
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
                405 - If Internal Conversion of Applicant to Employee Fails \n
                424 - If Creds Notification Email or Notice to the Front End Fails \n
                201 - On Successful hiring and notification\n
    Raises:
        ValueError: If the 'pk' value is invalid or not provided in the request.
        DoesNotExist: If the employment application with the provided 'pk' does not exist.
    """
    # Condition Checked: Requesting User is Logged in and An Admin
    if not request.user.is_authenticated or not request.user.is_superuser:
        logger.warning(
            f"No Authenticated or Non-Admin Hire Request Recieved - Denying Request"
        )
        return HttpResponse(
            status=get_status_code_for_unauthorized_or_forbidden(request),
            content=get_content_for_unauthorized_or_forbidden(request),
        )
    # Condition Checked: POST REQUEST  is vaild with a interger PK in body in key `pk`
    try:
        pk = int(request.POST.get("pk"))  # type: ignore
        logger.debug(f"Hire Request Initated for Employee ID: {pk}")
    except (ValueError, TypeError):
        logger.warning(
            "Bad Request to Hire Applicant, Invalid or NO Applcation PK Submitted"
        )
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
        logger.debug(
            f"Hire Request Resolving to {applicant.last_name}, {applicant.first_name}"
        )
    except EmploymentApplicationModel.DoesNotExist:
        logger.error("Failed to hire applicant. Employment application not found.")
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=bytes(
                "Failed to hire applicant. Employment application not found.", "utf-8"
            ),
        )
    # Condition Checked: An Corrosponding Employee Model Instance is created via the .hire_applicant method on the EmploymentApplicationModel class
    try:
        hired_user = applicant.hire_applicant(hired_by=request.user)  # type: ignore
        logger.debug(f"Created User Account. Returning: {hired_user}")
    except Exception as e:
        logger.error(f"Failed to hire applicant. Error: {e}")
        return HttpResponse(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=bytes(f"Failed to hire applicant. Error: {e}.", "utf-8"),
        )
    # Condition Checked: New User Creds are Sent VIA email and Frontend has been provided confirmation
    try:
        applicant.save()
        send_new_user_credentials(
            new_user_email=hired_user["user"]["email"],  # type: ignore
            new_user_first_name=hired_user["first_name"],
            password=hired_user["plain_text_password"],
            username=hired_user["username"],
        )
        content = f"username: {hired_user['username']},  password: {hired_user['plain_text_password']}, employee_id: {hired_user['employee_id']}"
        logger.success(
            f"Successfully Converted Appicant to Employee - {hired_user.last_name}, {hired_user.last_name}"
        )
        return HttpResponse(
            status=status.HTTP_201_CREATED, content=bytes(content, "utf-8")
        )
    except Exception as e:
        logger.exception(f"Failed to send new user credentials. Error: {e}")
        return HttpResponse(
            status=status.HTTP_424_FAILED_DEPENDENCY,
            content=bytes(f"Failed to send new user credentials. Error: {e}.", "utf-8"),
        )


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
        logger.warning(
            f"No Authenticated or Non-Admin Termination Request Recieved - Denying Request"
        )
        return HttpResponse(
            status=get_status_code_for_unauthorized_or_forbidden(request),
            content=get_content_for_unauthorized_or_forbidden(request),
        )
    # Condition Checked: POST REQUEST  is vaild with a interger PK in body in key `pk`
    try:
        pk = request.POST.get("pk")
        logger.debug(f"Termination Request Initated for Employee ID: {pk}")
    except (ValueError, TypeError):
        logger.info(
            "Bad Request to Hire Applicant, Invaild or NO Applcation PK Submitted"
        )
        return HttpResponse(
            status=400,
            content="Failed to terminate employee. Invalid or no 'pk' value provided in the request.",
        )
    # Condition Checked: Provided PK Employee ID associated with an Employee Instance
    try:
        terminated_employee = Employee.objects.get(id=pk)
        logger.debug(
            f"Termination Request Resolving to {terminated_employee.last_name}, {terminated_employee.first_name}"
        )
    except Employee.DoesNotExist:
        logger.info(f"Failed to hire applicant. Employment application not found.")
        return HttpResponse(
            status=404, content="Failed to terminate employee.. Employee not found."
        )
    # Condition Checked: An Corrosponding Employee Model Instance is created via the .terminate_employment method on the Employee class
    try:
        terminated_employee.terminate_employment()
        logger.success(
            f"employment status for {terminated_employee.last_name}, {terminated_employee.first_name} TERMINATED"
        )
        return HttpResponse(status=204)
    except Exception as e:
        logger.exception(f"Failed to terminate employee. Error: {e}.")
        return HttpResponse(
            status=400, content=f"Failed to terminate employee.. Error: {e}."
        )


class DetailedEmployeeView:
    pass


def employee_details(request, pk):
    if request.user.is_staff:
        context = dict()
        context["data"] = Employee.objects.get(id=pk)
        context["compliance"] = Compliance.objects.get(employee=pk)
        user = context["data"]
        compliance = context["compliance"]

        if request.method == "POST":
            user = Employee.objects.get(id=pk)
            compliance = Compliance.objects.get(employee=pk)
            form = EmployeeForm(
                request.POST,
                request.FILES,
                instance=Employee.objects.get(id=pk),
            )
            if form.has_changed:
                if form.is_valid:
                    form.save()
                    return redirect(reverse("profile"))

        elif request.method == "GET":
            context["compliance"] = Compliance.objects.get(employee=pk)
            context["form"] = EmployeeForm(instance=Employee.objects.get(id=pk))
            return render(
                request=request,
                template_name="home/employee-details.html",
                context=context,
            )
    else:
        raise PermissionDenied()


def force_pwd_login(request, *args, **kwargs):
    response = login(request, *args, **kwargs)
    if response.status_code == 302:
        # We have a user
        try:
            if request.user.get_profile().force_password_change:
                return redirect("django.contrib.auth.views.password_change")
        except AttributeError:  # No profile?
            pass
    return response
