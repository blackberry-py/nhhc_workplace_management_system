"""
Module: web_views.py
Description: This module contains views for rendering web pages, processing form data, and sending email notifications.
"""

from functools import cached_property

from django.conf import settings
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from django_require_login.mixins import PublicViewMixin, public
from formset.views import FormView
from loguru import logger

from applications.web.forms import ClientInterestForm, EmploymentApplicationForm
from applications.web.models import ClientInterestSubmission, EmploymentApplicationModel
from applications.web.tasks import process_new_application, process_new_client_interest
from common.cache import CachedResponseMixin, CachedTemplateView
from common.metrics import metrics

CACHE_TTL: int = settings.CACHE_TTL


# SECTION - Page Rendering Views
@method_decorator(require_safe, name="dispatch")
class HomePageView(CachedResponseMixin, PublicViewMixin, CachedTemplateView):
    template_name = "index.html"
    extra_context = {"title": "Home"}
    primary_model = None
    cache_models = [None]


@method_decorator(require_safe, name="dispatch")
class AboutUsView(CachedResponseMixin, PublicViewMixin, CachedTemplateView):
    template_name = "about.html"
    extra_context = {"title": "About Nett Hands"}
    primary_model = None
    cache_models = [None]


@method_decorator(require_safe, name="dispatch")
class SuccessfulSubmission(CachedResponseMixin, PublicViewMixin, CachedTemplateView):
    template_name = "submission.html"
    extra_context = {"title": "About Nett Hands"}
    primary_model = None
    cache_models = [None]


from functools import cached_property


class ClientInterestFormView(CachedResponseMixin, PublicViewMixin, FormView):
    """Manages client interest form submissions through a web interface.

    This view handles the complete lifecycle of a client interest form, from initial rendering to processing valid submissions. It provides a comprehensive workflow for capturing and validating client service requests.

    Attributes:
        form_class (ClientInterestForm): Form used for capturing client interest data.
        model (ClientInterestSubmission): Database model for storing client interest submissions.
        primary_model (ClientInterestSubmission): Primary model associated with the view.
        template_name (str): HTML template for rendering the client interest form.
        success_url (str): URL to redirect after successful form submission.
        extra_context (dict): Additional context data for template rendering.

    Methods:
        empty_form: Cached property that initializes a clean form instance.
        form_valid: Processes and saves a valid form submission.
        get: Renders the initial client interest form.
        post: Handles form submission, validation, and processing.
    """

    form_class = ClientInterestForm
    model = ClientInterestSubmission
    primary_model = ClientInterestSubmission
    cache_models = [None]
    template_name = "client-interest.html"
    client_interest_url = reverse_lazy("web:client_interest_form")
    success_url = reverse_lazy("web:form_submission_success")
    extra_context = {"title": "Client Services Request"}

    @cached_property
    def empty_form(self):
        return self.form_class()

    def form_valid(self, form: ClientInterestForm) -> HttpResponse:
        logger.debug("Form Is Valid")
        formdata = form.cleaned_data
        formdata["contact_number"] = str(formdata["contact_number"])
        form.save()
        process_new_client_interest.delay(formdata)
        return HttpResponsePermanentRedirect(self.success_url, {"type": "Client Interest Form"})

    @public
    def get(self, request):
        logger.debug({"form": self.empty_form})
        return render(request, self.template_name, {"form": self.empty_form})

    @public
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)

        metrics.increment_failed_submissions("client-interest")
        logger.warning(f"Form Failed Invalid: {form.errors.as_text}")
        return render(request, self.template_name, {"form": form, "form_errors": form.errors})


class EmploymentApplicationFormView(CachedResponseMixin, PublicViewMixin, FormView):
    """Handles employment application form submissions through a web interface.

    This view manages the entire lifecycle of an employment application form, from rendering the initial form to processing valid submissions. It provides a comprehensive workflow for capturing and validating employment interest applications.

    Attributes:
        model (EmploymentApplicationModel): The database model for storing employment applications.
        template_name (str): HTML template for rendering the employment application form.
        form_class (EmploymentApplicationForm): The form class used for capturing application data.
        success_url (str): URL to redirect after successful form submission.
        extra_context (dict): Additional context data for template rendering.
        primary_model (EmploymentApplicationModel): Primary model associated with the view.

    Methods:
        form: Cached property that initializes the form class.
        form_valid: Processes and saves a valid form submission.
        get_form: Dynamically retrieves or creates a form instance.
        get: Renders the initial employment application form.
        post: Handles form submission, validation, and processing.
    """

    model = EmploymentApplicationModel
    template_name = "employee-interest.html"
    form_class = EmploymentApplicationForm
    success_url = reverse_lazy("web:form_submission_success")
    extra_context = {"title": "Employment Application"}
    primary_model = EmploymentApplicationModel

    @cached_property
    def empty_form(self):
        return self.form_class()

    def form_valid(self, form, resume=None) -> HttpResponse:
        logger.debug("Form Is Valid")
        formdata = form.cleaned_data
        formdata["contact_number"] = str(form["contact_number"])
        form.save()

        if resume:
            formdata["resume_cv"] = resume.name

        process_new_application.delay(formdata)

        return HttpResponseRedirect(self.success_url, {"type": "Employment Interest Form"})

    def get_form(self, form_class=None):
        return self.form_class(self.request.POST, self.request.FILES) if self.request.POST else self.empty_form

    @public
    def get(self, request):
        return render(request, self.template_name, {"form": self.empty_form})

    @public
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            if resume := request.FILES.get("resume_cv"):
                logger.debug(f"Resume file uploaded: {resume.name}")
                return self.form_valid(form, resume)
            return self.form_valid(form)

        metrics.increment_failed_submissions("employment-application")
        logger.warning(f"Form Failed Invalid: {form.errors.as_text}")
        return render(request, self.template_name, {"form": form, "form_errors": form.errors})


@public
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
