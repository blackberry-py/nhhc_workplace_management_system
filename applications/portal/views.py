"""
module: portal.views

Functions:
- portal_dashboard: Renders the portal dashboard page.
- profile: Renders the user profile page and allows users to update their profile information.
- all_client_inquiries: Retrieves all client inquiries and returns them as JSON.
- marked_reviewed: Marks a client inquiry as reviewed.
- coming_soon: Renders a "coming soon" page.

Classes:
- ClientInquiriesListView: Renders a list of client inquiries.
- ClientInquiriesDetailView: Renders details of a specific client inquiry.
- EmploymentApplicationListView: Renders a list of submitted employment applications.
- EmploymentApplicationDetailView: Renders details of a specific employment application.
"""

from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from formset.calendar import CalendarResponseMixin
from formset.upload import FileUploadMixin

from applications.announcements.models import Announcements
from applications.employee.forms import EmployeeForm
from applications.employee.models import Employee
from applications.portal.forms import PayrollExceptionForm
from applications.portal.models import PayrollException
from applications.web.models import ClientInterestSubmission, EmploymentApplicationModel
from common.cache import CachedResponseMixin, NeverCacheMixin


class Dashboard(CalendarResponseMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        recent_announcements = list(Announcements.objects.all().filter(status="A").order_by("-date_posted")[:5])
        listed_announcements = []
        for announcement in list(recent_announcements):
            announcement = model_to_dict(announcement)
            announcement["posted_by"] = Employee.objects.get(employee_id=announcement["posted_by"]).first_name
            listed_announcements.append(announcement)
        context["recent_announcements"] = listed_announcements
        context["ExceptionForm"] = PayrollExceptionForm()
        return context


class ProfileDetailView(CachedResponseMixin, DetailView):
    model = Employee
    primary_model = Employee
    cache_models = []
    template_name = "profile_main.html"

    def get_object(self, queryset=None):
        queryset = Employee.objects.get(pk=self.request.user.employee_id)
        return queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        initial = model_to_dict(self.get_object())
        context["form"] = EmployeeForm(initial=initial)
        return context


class ProfileFormView(CachedResponseMixin, UpdateView, FileUploadMixin):
    form_class = EmployeeForm
    model = Employee
    primary_model = Employee
    cache_models = []
    template_name = "profile_main.html"

    def get_object(self, queryset=None):
        queryset = Employee.objects.get(pk=self.request.user.employee_id)
        return queryset

    def get_success_url(self):
        return reverse("profile")


class PayrollExceptionView(CachedResponseMixin, FormView):
    template_name = "exception.html"
    form_class = PayrollExceptionForm
    primary_model = PayrollException
    cache_models = []


class Profile(NeverCacheMixin, View):
    def get(self, request, *args, **kwargs):
        view = ProfileDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProfileFormView.as_view()
        return view(request, *args, **kwargs)


# TODO: Implement REST endpoint with DRF


# SECTION - Class-Based Views
class ClientInquiriesListView(CachedResponseMixin, ListView):
    """
    Renders a list of client inquiries.
    """

    template_name = "service-inquiries.html"
    model = ClientInterestSubmission
    primary_model = model
    cache_models = []
    queryset = ClientInterestSubmission.objects.all().order_by("-date_submitted")
    context_object_name = "submissions"
    paginate_by = 25

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context["unresponsed"] = ClientInterestSubmission.objects.filter(reviewed=False).count()
        context["showSearch"] = True
        context["reviewed"] = ClientInterestSubmission.objects.filter(
            reviewed=True,
        ).count()
        context["all_submissions"] = ClientInterestSubmission.objects.all().count()
        context["type_of_submission"] = "Client Service Request"
        return context


class ClientInquiriesDetailView(CachedResponseMixin, DetailView):
    """
    Renders details of a specific client inquiry.
    """

    template_name = "submission-details.html"
    model = ClientInterestSubmission
    primary_model = model
    cache_models = []
    context_object_name = "submission"
    pk_url_kwarg = "pk"
    extra_context = {"type_of_submission": "Client Service Request"}


class EmploymentApplicationListView(CachedResponseMixin, ListView):
    """
    Renders a list of submitted employment applications.
    """

    template_name = "submitted-applications.html"
    model = EmploymentApplicationModel
    primary_model = model
    cache_model = []
    queryset = EmploymentApplicationModel.objects.all().order_by("-date_submitted")
    context_object_name = "submissions"
    paginate_by = 25

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context["unresponsed"] = EmploymentApplicationModel.objects.filter(reviewed=False).count()
        context["reviewed"] = EmploymentApplicationModel.objects.filter(
            reviewed=True,
        ).count()
        context["all_submissions"] = EmploymentApplicationModel.objects.count()
        context["type_of_submission"] = "Employment Application"

        return context


class EmploymentApplicationDetailView(DetailView):
    """
    Renders details of a specific employment application.
    """

    template_name = "applicant-details.html"
    model = EmploymentApplicationModel
    context_object_name = "submission"
    pk_url_kwarg = "pk"
    extra_context = {"type_of_submission": "Employment Application"}


# !SECTION - END OF CLASS-BASED VIEWS


class ExceptionView(View):
    def get(self, request):
        pass


# !SECTION - END OF AJAX HOOKS

# SECTION - Temp Endpoints
# TODO: Remove this once the features they are Referencing is implemented.


@login_required(login_url="/login/")
def coming_soon(request) -> HttpResponse:
    """
    Renders a "coming soon" page.

    Returns:
    - HttpResponse: Rendered HTML template
    """
    return render(request, "coming_soon.html", {})
