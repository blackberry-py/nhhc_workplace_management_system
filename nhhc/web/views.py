"""
Module: web_views.py
Description: This module contains views for rendering web pages, processing form data, and sending email notifications.
"""

from django.conf import settings
from django.forms import model_to_dict
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import render, reverse
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from django_require_login.mixins import PublicViewMixin, public
from formset.views import FormView
from loguru import logger
from prometheus_client import Counter
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from web.tasks import process_new_application, process_new_client_interest

from nhhc.utils.cache import CachedResponseMixin
from nhhc.utils.helpers import CachedTemplateView
from nhhc.utils.upload import S3HANDLER

CACHE_TTL: int = settings.CACHE_TTL

failed_submission_attempts = Counter("failed_submission_attempts", "Metric Counter for the Number of Application or Client Interest Submission attempts that failed validation", ["application_type"])


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


class ClientInterestFormView(CachedResponseMixin, PublicViewMixin, FormView):
    form_class = ClientInterestForm
    model = ClientInterestSubmission
    primary_model = ClientInterestSubmission
    cache_models = [None]
    template_name = "client-interest.html"
    success_url = reversed("web:form_submission_success")
    extra_context = {"title": "Client Services Request"}

    def form_valid(self, form: ClientInterestForm) -> HttpResponse:
        """If the form is valid, redirect to the supplied URL."""
        logger.debug("Form Is Valid")
        form.save()
        process_new_client_interest(form.cleaned_data)
        return HttpResponsePermanentRedirect(reverse("web:form_submission_success"), {"type": "Client Interest Form"})
        
    @public
    def get(self, request):
        form = ClientInterestForm()
        context = {"form": form}
        logger.debug(context)
        return render(request, "client-interest.html", context)

    @public
    def post(self, request):
        context = {}
        form = ClientInterestForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        elif not form.is_valid():
            context = {"form": self.get_form()}
            context["form_errors"] = form.errors
            failed_submission_attempts.labels(application_type="client-interest").inc()
            logger.error("Form Is Invalid")
            return HttpResponseRedirect(reverse("web:client_interest_form"), {"errors": form.errors})



class EmploymentApplicationFormView(CachedResponseMixin, PublicViewMixin, FormView):
    model = EmploymentApplicationModel
    template_name = "employee-interest.html"
    success_url = reversed("web:form_submission_success")
    extra_context = {"title": "Employment Application"}
    primary_model = EmploymentApplicationModel

    def form_valid(self, form: EmploymentApplicationForm, resume=None) -> HttpResponse:
        logger.debug("Form Is Valid")
        formdata = form.cleaned_data
        formdata["contact_number"] = str(form["contact_number"])
        if resume is not None:
            formdata["resume_cv"] = resume.file.path
        process_new_application.delay(formdata)
        form.save()
        return HttpResponseRedirect(reverse("web:form_submission_success"), {"type": "Employment Interest Form"})

    def get_form(self, form_class=None):
        if self.request.POST:
            return EmploymentApplicationForm(self.request.POST, self.request.FILES)
        else:
            return EmploymentApplicationForm()
                                    
    @public
    def get(self, request):
        form = EmploymentApplicationForm()
        context = {"form": form}
        logger.debug(context)
        return render(request, "employee-interest.html", context)

    @public
    def post(self, request):
        context = {}
        form = EmploymentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES.get('resume_cv'):
                resume = request.FILES['resume_cv']
                return self.form_valid(form, resume)
            return self.form_valid(form)
     
        context = {"form": self.get_form()}
        context["form_errors"] = form.errors
        logger.warning(f'Form Failed Invalid: {form.errors.as_text}')
        failed_submission_attempts.labels(application_type="employment").inc()
        return HttpResponseRedirect(reverse("web:employment_application_form"), context)


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
