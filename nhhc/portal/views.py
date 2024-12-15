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

import json
from typing import Any, Dict

from announcements.models import Announcements
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django_filters.rest_framework import DjangoFilterBackend
from employee.forms import EmployeeForm
from employee.models import Employee
from formset.calendar import CalendarResponseMixin
from formset.upload import FileUploadMixin
from loguru import logger
from portal.forms import PayrollExceptionForm
from portal.models import PayrollException
from portal.serializers import ClientInquiriesSerializer
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from web.models import ClientInterestSubmission, EmploymentApplicationModel

from nhhc.utils.cache import CachedResponseMixin
from nhhc.utils.helpers import NeverCacheMixin


class Dashboard(CalendarResponseMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        recent_annoucements = list(Announcements.objects.all().filter(status="A").order_by("-date_posted")[:5])
        listed_amnnoucements = []
        for announcement in list(recent_annoucements):
            announcement = model_to_dict(announcement)
            announcement["posted_by"] = Employee.objects.get(employee_id=announcement["posted_by"]).first_name
            listed_amnnoucements.append(announcement)
        context["recent_announcements"] = listed_amnnoucements
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


class EmploymentApplicationModelAPIListView(CachedResponseMixin, mixins.DestroyModelMixin, generics.ListCreateAPIView):
    queryset = EmploymentApplicationModel.objects.all()
    serializer_class = [EmploymentApplicationModel]
    primary_model = EmploymentApplicationModel
    cache_model = [Employee, EmploymentApplicationModel]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "reviewed",
        "hired",
        "home_address2",
        "city",
        "state",
        "zipcode",
        "mobility",
        "prior_experience",
        "ipdh_registered",
        "availability_monday",
        "availability_tuesday",
        "availability_wednesday",
        "availability_thursday",
        "availability_friday",
        "availability_saturday",
        "availability_sunday",
        "reviewed",
        "hired",
        "reviewed_by",
        "date_submitted",
    ]

    def destroy(self, request, instance):
        if request.user.is_superuser is False:
            return Response(
                data="Only Managers can preform a delete operation",
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def all_client_inquiries(request: HttpRequest) -> HttpResponse:
    """
    Retrieves all client inquiries and returns them as JSON.

    Returns:
    - HttpResponse: JSON response containing all client inquiries
    """
    inquiries = ClientInterestSubmission.objects.all().values()
    inquiries_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=inquiries_json, status=status.HTTP_200_OK)


class ClientInquiriesAPIListView(CachedResponseMixin, generics.ListCreateAPIView):
    queryset = ClientInterestSubmission.objects.all()
    primary_model = ClientInterestSubmission
    cache_models = []
    serializer_class = ClientInquiriesSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    filter_backends = [DjangoFilterBackend]


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


# TODO: Implement REST endpoint with DRF
@login_required(login_url="/login/")
def all_applicants(request: HttpRequest) -> HttpResponse:
    """
    Retrieves all employment applications and returns them as JSON.

    Returns:
    - HttpResponse: JSON response containing all employment applications
    """
    inquiries = EmploymentApplicationModel.objects.all().values()
    for inquiry in inquiries:
        inquiry["contact_number"] = str(inquiry["contact_number"])
    applicant_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=applicant_json, status=200)


# !SECTION - END OF CLASS-BASED VIEWS


# SECTION - AJAX Hooks
def marked_reviewed(request):
    """
    Marks a client inquiry as reviewed.

    Returns:
    - HttpResponse: Success or error response
    """
    try:
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        pk = body["pk"]
        submission = ClientInterestSubmission.objects.get(id=pk)
        submission.marked_reviewed(request.user)
        submission.save()
        logger.info(f"{submission.id} marked as reviewed")
        return HttpResponse(status=204)
    except json.decoder.JSONDecodeError:
        logger.error("Error decoding request data")
        return HttpResponse(status=400)
    except ObjectDoesNotExist as no_object:
        logger.error(f"Object with pk {pk} Does Not Exist, Unable to Mark Reviewed")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"ERROR: Unable to Mark {submission.id} REVIEWED: {e}")
        return HttpResponse(status=500)


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
