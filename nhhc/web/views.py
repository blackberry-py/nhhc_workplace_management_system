"""
Module: web_views.py
Description: This module contains views for rendering web pages, processing form data, and sending email notifications.
"""

from django.conf import settings
from django.forms import model_to_dict
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from formset.views import FormView
from loguru import logger
from prometheus_client import Counter
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from web.tasks import process_new_application, process_new_client_interest
from nhhc.utils.helpers import CachedTemplateView
from django_require_login.mixins import PublicViewMixin, public

CACHE_TTL: int = settings.CACHE_TTL


# SECTION - Page Rendering Views
@method_decorator(require_safe, name="dispatch")
class HomePageView(PublicViewMixin, CachedTemplateView):
    template_name = "index.html"
    extra_context = {"title": "Home"}


@method_decorator(require_safe, name="dispatch")
class AboutUsView(PublicViewMixin, CachedTemplateView):
    template_name = "about.html"
    extra_context = {"title": "About Nett Hands"}


@method_decorator(require_safe, name="dispatch")
class SuccessfulSubmission(PublicViewMixin, CachedTemplateView):
    template_name = "submission.html"
    extra_context = {"title": "About Nett Hands"}


class ClientInterestFormView(PublicViewMixin, FormView):
    form_class = ClientInterestForm
    model = ClientInterestSubmission
    template_name = "client-interest.html"
    success_url = reversed("submitted")
    extra_context = {"title": "Client Services Request"}

    def form_valid(self, form: ClientInterestForm) -> HttpResponse:
        failed_submission_attempts_client = Counter("failed_submission_attempts_client", "Metric Counter for the Number of Failed Submission attempts that failed validation")

        """If the form is valid, redirect to the supplied URL."""
        if form.is_valid():
            logger.debug("Form Is Valid")
            form.save()
            process_new_client_interest(form.cleaned_data)
            return HttpResponsePermanentRedirect(reverse("submitted"), {"type": "Client Interest Form"})
        else:
            failed_submission_attempts_client.inc()
            logger.error(f"Form Is Invalid: {form.errors.as_text()}")
            return HttpResponseRedirect(reverse_lazy("client_interest"), {"errors": form.errors.as_data()})

    @public
    def get(self, request):
        form = ClientInterestForm()
        context = {"form": form}
        return render(request, "client-interest.html", context)

    @public
    def post(self, request):
        context = {}
        form = ClientInterestForm(request.POST)
        if form.is_valid():
            self.form_valid(form)
        elif not form.is_valid():
            context["form"] = form
            context["form_errors"] = form.errors
            return render(request, "client-interest.html", context)


class EmploymentApplicationFormView(PublicViewMixin, FormView):
    model = EmploymentApplicationModel
    template_name = "employee-interest.html"
    success_url = reversed("submitted")
    extra_context = {"title": "Employment Application"}

    def form_valid(self, form: EmploymentApplicationForm) -> HttpResponse:
        failed_submission_attempts_application = Counter("failed_submission_attempts_application", "Metric Counter for the Number of Applicatioin Submission attempts that failed validation")
        """If the form is valid, redirect to the supplied URL."""
        if form.is_valid():
            return self.process_submitted_application(form)
        failed_submission_attempts_application.inc()
        logger.error("Form Is Invalid")
        return HttpResponsePermanentRedirect(reverse("application"), {"errors": form.errors.as_data()})

    def process_submitted_application(self, form):
        logger.debug("Form Is Valid")
        form.cleaned_data["contact_number"] = str(form["contact_number"])
        form.save()
        processed_form = form.cleaned_data
        del processed_form["resume_cv"]
        process_new_application(processed_form)
        return HttpResponsePermanentRedirect(reverse("submitted"), {"type": "Employment Interest Form"})

    def get_form(self, form_class=None):
        if self.request.POST:
            return EmploymentApplicationForm(self.request.POST)
        else:
            return EmploymentApplicationForm()

    @public
    def get(self, request):
        form = EmploymentApplicationForm()
        context = {"form": form}
        logger.debug(context)
        return render(request, "client-interest.html", context)

    @public
    def post(self, request):
        context = {}
        form = EmploymentApplicationForm(request.POST)
        if form.is_valid():
            self.form_valid(form)
        elif not form.is_valid():
            context["form"] = form
            context["form_errors"] = form.errors
            return render(request, "client-interest.html", context)


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
