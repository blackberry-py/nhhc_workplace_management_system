import json
import os
from django.conf import settings
from django.forms import model_to_dict
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from django.urls import reverse_lazy
from formset.views import FormView
from loguru import logger
from web.forms import ClientInterestForm, EmploymentApplicationForm
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from web.tasks import process_new_application, process_new_client_interest
from nhhc.utils.helpers import CachedTemplateView
from django_require_login.mixins import PublicViewMixin, public
from django.core.exceptions import ValidationError
from nhhc.utils.metrics import INVALID_APPLICATIONS, FAILED_SUBMISSIONS
CACHE_TTL: int = settings.CACHE_TTL

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
    extra_context = {"title": "Submission Successful"}

class ClientInterestFormView(PublicViewMixin, FormView):
    form_class = ClientInterestForm
    model = ClientInterestSubmission
    template_name = "client-interest.html"
    success_url = reverse_lazy("submitted")
    extra_context = {"title": "Client Services Request", "GOOGLE_MAPS_API_KEY": os.environ['GOOGLE_MAPS_API_KEY']}

    def process_submitted_client_interest(self, form: ClientInterestForm):
        logger.debug("ClientInterestForm is valid")
        if form.cleaned_data["contact_number"]:
            form.cleaned_data["contact_number"] = str(form.cleaned_data["contact_number"])
        try:        
            form.save()
            processed_form = form.cleaned_data
            process_new_application(processed_form)
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            logger.error(f"Error processing client interest form: {e}")
            return self.render_to_response(self.get_context_data(form=form, form_errors=e, **self.extra_context))

    def form_valid(self, form: ClientInterestForm):
        return self.process_submitted_client_interest(form)
    def form_invalid(self, form):
        logger.error(f"ClientInterestForm is invalid. Errors: {form.errors.as_json()}")
        FAILED_SUBMISSIONS.inc()
        return self.render_to_response(self.get_context_data(form=form, form_errors=form.errors,  **self.extra_context))

    @public
    def get(self, request):
        form = ClientInterestForm()                                    
        context = {"form": form}
        return render(request, "client-interest.html", context)


class EmploymentApplicationFormView(PublicViewMixin, FormView):
    form_class = EmploymentApplicationForm
    model = EmploymentApplicationModel
    template_name = "employee-interest.html"
    success_url = reverse_lazy("submitted")
    extra_context = {"title": "Employment Application", "GOOGLE_MAPS_API_KEY": os.environ['GOOGLE_MAPS_API_KEY']}

    def process_submitted_application(self, form):
        logger.debug("EmploymentApplicationForm is valid")
        # if form.data["contact_number"]:
        #     form.data["contact_number"] = str(form.data["contact_number"])
        try:
            form.save()
            processed_form = form.cleaned_data
            if processed_form["resume_cv"]:
                del processed_form["resume_cv"]
            process_new_application(processed_form)
            return HttpResponseRedirect(self.success_url)

        except Exception as e:
            logger.error(f"Error processing form: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error(f"EmploymentApplicationForm is invalid. Errors: {form.errors.as_json()}")
        INVALID_APPLICATIONS.inc()
        return self.render_to_response(self.get_context_data(form=form, form_errors=form.errors,  **self.extra_context))

    def form_valid(self, form: EmploymentApplicationForm):
        return self.process_submitted_application(form)

    @public
    def get(self, request):
        form = EmploymentApplicationForm()
        context = {"form": form}
        return render(request, "employee-interest.html", context)

[]
@public
@cache_page(CACHE_TTL)
def favicon(request: HttpRequest) -> HttpResponse:
    favicon_file = static("img/favicon.ico")
    return FileResponse(favicon_file)
