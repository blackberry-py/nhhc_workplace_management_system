"""
Module: web_views.py
Description: This module contains views for rendering web pages, processing form data, and sending email notifications.
"""
import os
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from string import Template
from typing import Union

from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.templatetags.static import static
from django.views.decorators.cache import cache_page
from django.views.generic.edit import FormView
from loguru import logger
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from nhhc.utils.email_templates import APPLICATION_BODY, CLIENT_BODY
from nhhc.utils.helpers import CachedTemplateView
from nhhc.utils.mailer import PostOffice

CACHE_TTL: int = settings.CACHE_TTL


# SECTION - Page Rendering Views
class HomePageView(CachedTemplateView):
    template_name = "index.html"
    extra_context = {"title": "Home"}
    http_method_names = ["get", "head", "trace"]


class AboutUsView(CachedTemplateView):
    template_name = "about.html"
    extra_context = {"title": "About Nett Hands"}
    http_method_names = ["get", "head", "trace"]


class ClientInterestFormView(FormView):
    form_class = ClientInterestForm
    model = ClientInterestSubmission
    template_name = "client-interest.html"
    success_url = "/submitted"
    extra_context = {"title": "Client Services Request"}


class EmploymentApplicationFormView(FormView):
    form_class = EmploymentApplicationForm
    model = EmploymentApplicationModel
    template_name = "employee-interest.html"
    success_url = reversed("submitted")
    extra_context = {"title": "Employment Application"}

    def form_valid(self, form: EmploymentApplicationForm) -> HttpResponseRedirect:
        """If the form is valid, redirect to the supplied URL."""
        if form.is_valid():
            logger.debug("Form Is Valid")
            form.save()
            return HttpResponseRedirect(reverse("submitted"))
        else:
            logger.error("Form Is Invalid")
            return HttpResponseRedirect(reverse("employment-application", {"errors": form.errors}))


@cache_page(CACHE_TTL)
def favicon(request: HttpRequest) -> HttpResponse:
    """
    This function returns the favicon file as a response.

    Parameters:
    - request: HttpRequest object

    Returns:
    - HttpResponse object
    """
    favicon_file = static("img/favicon.ico")
    return FileResponse(filename=favicon_file)


#!SECTION

# SECTION - Internal Functional View


def send_external_application_submission_confirmation(form: Union[ClientInterestForm, EmploymentApplicationForm]) -> None:
    """
    Class method to send email notification of the submissions of client interest and employment application forms

    Args:
        form (ClientInterestForm | EmploymentApplicationForm): The form containing the submitted information.

    Returns:
        None

    Raises:
        Exception: If the email transmission fails.
    """
    try:
        sender_email: str = os.getenv("NOTIFICATION_SENDER_EMAIL")
        sender_password: str = os.getenv("EMAIL_ACCT_PASSWORD")
        recipient_email: str = form.cleaned_data["email"].lower()
        subject: str = f"Thanks For Your Employment Interest, {form.cleaned_data['first_name']}!"
        content: str = APPLICATION_BODY

        html_message: MIMEText = MIMEText(content, "html")
        html_message["Subject"]: str = subject
        html_message["From"]: str = sender_email
        html_message["To"]: str = recipient_email
        with smtplib.SMTP_SSL(
            os.getenv("EMAIL_SERVER"),
            os.getenv("EMAIL_SSL_PORT"),
        ) as server:
            server.login(sender_email, sender_password)
            transmission = server.sendmail(
                sender_email,
                recipient_email,
                html_message.as_string(),
            )
            applicant = form.cleaned_data["last_name"], form.cleaned_data["first_name"]
            log_message = f"Application Submitted - {applicant} - {recipient_email} - Successful"
            logger.info(log_message)
            return transmission
    except Exception as e:
        applicant = form.cleaned_data["last_name"], form.cleaned_data["first_name"]
        log_message = f"Application Submitted - {applicant} - {recipient_email} - FAILED: {e}"
        logger.error(log_message)


def send_internal_application_submission_confirmation(
    form: ClientInterestForm | EmploymentApplicationForm,
) -> None:
    """
    Sends a confirmation email for a new employment interest or client interest submission.

    Args:
        form (ClientInterestForm | EmploymentApplicationForm): The form containing the submitted information.

    Returns:
        None

    Raises:
        Exception: If the email transmission fails.
    """
    try:
        sender_email = os.getenv("NOTIFICATION_SENDER_EMAIL")
        recipient_email = os.getenv("NOTIFICATION_Application_SUBMISSION_EMAIL")
        sender_password = os.getenv("EMAIL_ACCT_PASSWORD")
        subject = f"New Employment Interest - {form.cleaned_data['last_name']}, {form.cleaned_data['first_name']}"
        message = EmailMessage()
        message["Subject"] = subject
        message["To"] = recipient_email
        content_template = Template(
            """
            Attention: A New Employment Interest has Been Submitted, the application information is as follows: \n
            First Name: $first_name\n
            Last Name: $last_name\n
            E-mail: $email\n
            Contact Number: $contact_number\n
            Street Address: $home_address\n
            City: $city\n
            State: $state\n
            Zipcode: $zipcode\n
            Mobility: $mobility\n
            Prior Experience: $prior_experience\n
            Available Monday: $availability_monday\n
            Availability Tuesday: $availability_tuesday\n
            Availability Wednesday: $availability_wednesday\n
            Availability Thursday: $availability_thursday\n
            Availability Friday: $availability_friday\n
            Availability Saturday: $availability_saturday\n
            Availability Sunday: $availability_sunday\n
            """,
        )
        content = content_template.substitute(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
            contact_number=form.cleaned_data["contact_number"],
            home_address=form.cleaned_data["home_address"],
            city=form.cleaned_data["city"],
            state=form.cleaned_data["state"],
            zipcode=form.cleaned_data["zipcode"],
            mobility=form.cleaned_data["mobility"],
            prior_experience=form.cleaned_data["prior_experience"],
            availability_monday=form.cleaned_data["availability_monday"],
            availability_tuesday=form.cleaned_data["availability_tuesday"],
            availability_wednesday=form.cleaned_data["availability_wednesday"],
            availability_thursday=form.cleaned_data["availability_thursday"],
            availability_friday=form.cleaned_data["availability_friday"],
            availability_saturday=form.cleaned_data["availability_saturday"],
            availability_sunday=form.cleaned_data["availability_sunday"],
        )
        server_ssl = smtplib.SMTP_SSL(
            os.getenv("EMAIL_SERVER"),
            os.getenv("EMAIL_SSL_PORT"),
        )
        server_ssl.ehlo()
        server_ssl.login(
            os.getenv("NOTIFICATION_SENDER_EMAIL"),
            os.getenv("EMAIL_ACCT_PASSWORD"),
        )
        message.set_content(content)
        server_ssl.send_message(message)
        server_ssl.quit()
        applicant = form.cleaned_data["last_name"], form.cleaned_data["first_name"]
        logger.info(f"Internal Application Notice Sent -  {applicant} - Success")
    except Exception as e:
        applicant = form.cleaned_data["last_name"], form.cleaned_data["first_name"]
        logger.error(f"Internal Application Notice Sent -  {applicant} -   FAILED: {e}")


def send_external_client_submission_confirmation(form):
    """Internal Non-Rendering View Function to send email notification of the submissions of client interest and employment application forms

    Args:
        form: Form Instance
    """
    applicant = form.cleaned_data["last_name"], form.cleaned_data["first_name"]
    try:
        sender_email = os.getenv("NOTIFICATION_SENDER_EMAIL")
        sender_password = os.getenv("EMAIL_ACCT_PASSWORD")
        recipient_email = form.cleaned_data["email"].lower()
        subject = f"We Got Your Client Interest {form.cleaned_data['first_name']}!"
        content = CLIENT_BODY

        html_message = MIMEText(content, "html")
        html_message["Subject"] = subject
        html_message["From"] = sender_email
        html_message["To"] = recipient_email
        with smtplib.SMTP_SSL(
            os.getenv("EMAIL_SERVER"),
            os.getenv("EMAIL_SSL_PORT"),
        ) as server:
            server.login(sender_email, sender_password)
            transmission = server.sendmail(
                sender_email,
                recipient_email,
                html_message.as_string(),
            )
            log_message = f"Interest Submitted - {applicant} - {recipient_email} - Successful"
            logger.info(log_message)
            return transmission
    except Exception as e:
        log_message = f"Interest Submitted - {applicant} - {recipient_email} - FAILED: {e}"
        logger.error(log_message)


def send_internal_client_submission_confirmation(form):
    """Internal Non-Rendering View Function to send email notification of the submissions of client interest and employment application forms
    Args:
        form: Form Instance
    """
    applicant = form.cleaned_data["last_name"], form.cleaned_data["first_name"]
    try:
        recipient_email = os.getenv("NOTIFICATION_CLIENT_SUBMISSION_EMAIL")
        subject = f"New Client Interest - {form.cleaned_data['last_name']}, {form.cleaned_data['first_name']}"
        message = EmailMessage()
        message["Subject"] = subject
        message["To"] = recipient_email
        content_template = Template(
            """
            Attention: A New Client Interest has Been Submitted, the application information is as follows: \n
            First Name: $first_name\n
            Last Name: $last_name\n
            E-mail: $email\n
            Contact Number: $contact_number\n
            Zipcode: $zipcode\n
            Insurance Carrier: $insurance_carrier\n
            Desired Service: $desired_service
            """,
        )
        content = content_template.substitute(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
            desired_service=form.cleaned_data["desired_service"],
            contact_number=form.cleaned_data["contact_number"],
            zipcode=form.cleaned_data["zipcode"],
            insurance_carrier=form.cleaned_data["insurance_carrier"],
        )
        server_ssl = smtplib.SMTP_SSL(
            os.getenv("EMAIL_SERVER"),
            os.getenv("EMAIL_SSL_PORT"),
        )
        server_ssl.ehlo()
        server_ssl.login(
            os.getenv("NOTIFICATION_SENDER_EMAIL"),
            os.getenv("EMAIL_ACCT_PASSWORD"),
        )
        message.set_content(content)
        server_ssl.send_message(message)
        server_ssl.quit()
        logger.info(f"Internal Interest Notice Sent -  {applicant} - Success")
    except Exception as e:
        logger.error(f"Internal Interest Notice Sent -  {applicant} -   FAILED: {e}")


# !SECTION
# SECTION - Form Processing Views
@cache_page(CACHE_TTL)
def client_interest(request):
    """Instantiates the ClientInterestForm Class and checks the request.method. If Post - Processes Form Data. If GET - Renders Form

    Args:
        request (object): Request Object Passed at time of calling.

    Returns:
        Renders wor Processes ClientInterestForm
    """
    context = dict()
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ClientInterestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            send_external_client_submission_confirmation(form)
            send_internal_client_submission_confirmation(form)
            return redirect("submitted")
        elif not form.is_valid():
            context["form"] = form
            context["form_errors"] = form.errors
            return render(request, "client-interest.html", context)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ClientInterestForm()
        context["form"] = form
        context["title"] = "Client Services Request"
        logger.debug(context)
        return render(request, "client-interest.html", context)


@cache_page(CACHE_TTL)
def employee_interest(request):
    """Instantiates the EmploymentApplicationForm Class and checks the request.method. If Post - Processes Form Data. If GET - Renders Form

    Args:
        request (HttpRequestObject): Request Object Passed at time of calling.

    Returns:
        Renders sub-page Employee Application Form
    """
    # if this is a POST request we need to process the form data
    context = dict()
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = EmploymentApplicationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            form.save()
            send_internal_application_submission_confirmation(form)
            PostOffice.send_external_application_submission_confirmation(form)
            return redirect("submitted", permanent=True)
        elif not form.is_valid():
            context["form"] = form
            context["form_errors"] = form.errors
            return render(request, "employee-interest.html", context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmploymentApplicationForm()
        context["form"] = form
        context["title"] = "Employment Application"
        return render(request, "employee-interest.html", context)


@cache_page(CACHE_TTL)
def submitted(request):
    return render(request, "submission.html", {"title": "Form Submission Confirmation"})


#!SECTION
