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

import csv
import json
import os

import arrow
from announcements.forms import AnnouncementForm
from announcements.models import Announcements
from typing import Dict
from cacheops import cached_view_as
from compliance.models import Compliance
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect, render, reverse
from django.template import loader
from django.urls import reverse
from django.views.generic.detail import DetailView
from employee.forms import EmployeeForm
from employee.models import Employee
from django.views.generic.list import ListView
from loguru import logger
from web.forms import ClientInterestForm
from web.models import ClientInterestSubmissions, EmploymentApplicationModel

now = arrow.now(tz="America/Chicago")
logger.add(
    settings.DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG"
)
logger.add(
    settings.PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO"
)
logger.add(
    settings.LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO"
)


@login_required(login_url="/login/")
def portal_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Renders the portal dashboard page.

    Retrieves new applications, client requests, and announcements to display on the dashboard.

    Args:
    - request: HTTP request object

    Returns:
    - HttpResponse: Rendered HTML template
    """
    context = dict()
    context["segment"] = "index"
    new_applications = EmploymentApplicationModel.objects.filter(
        reviewed=False
    ).order_by("-date_submitted")
    new_client_requests = ClientInterestSubmissions.objects.filter(
        reviewed=False
    ).order_by("-date_submitted")
    announcements = Announcements.objects.all().order_by("-date_posted")[:10]
    context["announcements"] = announcements
    context["new_applications"] = new_applications
    context["new_client_requests"] = new_client_requests
    html_template = loader.get_template("home/index.html")
    return HttpResponse(html_template.render(context, request))

# TODO: Convert to Class-Based
@login_required(login_url="/login/")
def profile(request: HttpRequest) -> HttpResponseRedirect:
    """
    Renders the user profile page and allows users to update their profile information.

    Retrieves user and compliance data to display on the profile page.

    Args:
    - request: HTTP request object

    Returns:
    - HttpResponse: Rendered HTML template
    """
    context = dict()
    context["data"] = Compliance.objects.select_related("employee").get(
        id=request.user.id
    )
    user = context["data"]

    if request.method == "POST":
        user = Employee.objects.get(username=request.user.username)
        form = EmployeeForm(
            request.POST,
            request.FILES or None,
            prefix="profile",
        )
        if form.has_changed:
            for changed_field in form.changed_data:
                user.changed_data = form.data.get(changed_field)
            user.save()
            return redirect(reverse("profile"))

    elif request.method == "GET":
        context["form"] = EmployeeForm(instance=request.user)
        context["compliance"] = Compliance.objects.get(employee=request.user)
        return render(
            request=request,
            template_name="home/profile.html",
            context=context,
        )

# TODO: Implement REST endpoint with DRF 
def all_client_inquiries(request: HttpRequest) -> HttpResponse:
    """
    Retrieves all client inquiries and returns them as JSON.

    Returns:
    - HttpResponse: JSON response containing all client inquiries
    """
    inquiries = ClientInterestSubmissions.objects.all().values()
    inquiries_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=inquiries_json, status=200)

# SECTION - Class-Based Views 
class ClientInquiriesListView(ListView):
    """
    Renders a list of client inquiries.
    """
    template_name = "home/service-inquiries.html"
    model = ClientInterestSubmissions
    queryset = ClientInterestSubmissions.objects.all().order_by("-date_submitted")
    context_object_name = "submissions"
    paginate_by = 25
    
    def get_context_data(self, **kwargs)  -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context["unresponsed"] = ClientInterestSubmissions.objects.filter(reviewed=False).count()
        context["showSearch"] = True
        context["reviewed"] = ClientInterestSubmissions.objects.filter(
        reviewed=True,
    ).count()
        context["all_submissions"] = ClientInterestSubmissions.objects.all().count()
        return context
        
class ClientInquiriesDetailView(DetailView):
    """
    Renders details of a specific client inquiry.
    """
    template_name = "home/submission-details.html"
    model = ClientInterestSubmissions
    context_object_name = "submission"
    pk_url_kwarg = "pk"




class EmploymentApplicationListView(ListView):
    """
    Renders a list of submitted employment applications.
    """
    template_name = "home/submitted-applications.html"
    model = EmploymentApplicationModel
    queryset = EmploymentApplicationModel.objects.all().order_by("-date_submitted")
    context_object_name = "submissions"
    paginate_by = 25
                                                                                                            
    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context["unresponsed"] = EmploymentApplicationModel.objects.filter(reviewed=False).count()
        context["reviewed"] = EmploymentApplicationModel.objects.filter(
        reviewed=True,
    ).count()
        context["all_submissions"] = EmploymentApplicationModel.objects.all().count()
        return context

class EmploymentApplicationDetailView(DetailView):
    """
    Renders details of a specific employment application.
    """
    template_name = "home/applicant-details.html"
    model = ClientInterestSubmissions
    context_object_name = "submission"
    pk_url_kwarg = "pk"

# TODO: Implement REST endpoint with DRF 
@login_required(login_url="/login/")
def all_applicants(request: Ht) -> HttpResponse:
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
        submission = ClientInterestSubmissions.objects.get(id=pk)
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
 that is all ladies