"""
Module:  portal.views
This module contains views for handling client inquiries, employment applications, and user profiles.

The module includes the following functions:
- index(request): Renders the home page with new job applications and announcements.
- profile(request): Handles user profile updates and displays user information.
- all_client_inquiries(request): Retrieves all client inquiries and returns them as JSON.
- client_inquiries(request): Renders the client inquiries page with the number of unreviewed submissions.
- submission_detail(request, pk): Renders the details of a specific client inquiry submission.
- marked_reviewed(request): Marks a client inquiry submission as reviewed.
- employment_applications(request): Renders the employment applications page with the number of unreviewed submissions.
- applicant_details(request, pk): Renders the details of a specific employment application submission.
- all_applicants(request): Retrieves all employment applications and returns them as JSON.
"""
import csv
import json
import os

import arrow
from announcements.forms import AnnouncementForm
from announcements.models import Announcements
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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.template import loader
from django.urls import reverse
from django.views.generic.detail import DetailView
from employee.forms import EmployeeForm
from employee.models import Employee
from django.views.generic.detail import DetailView
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
def portal_dashboard(request):
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


@login_required(login_url="/login/")
def profile(request):
    context = dict()
    context["data"] = Compliance.objects.select_related("employee").get(
        id=request.user.id
    )
    # context["compliance"] = Compliance.objects.get(employee_id=request.user.id)
    user = context["data"]
    compliance = context["compliance"]

    if request.method == "POST":
        user = Employee.objects.get(username=request.user.username)
        compliance = Compliance.objects.get(employee=request.user.is_staff)
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


def all_client_inquiries(request):
    inquiries = ClientInterestSubmissions.objects.all().values()
    inquiries_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=inquiries_json, status=200)


class ClientInquiriesListView(ListView):
    template_name = "home/service-inquiries.html"
    model = ClientInterestSubmissions
    queryset = ClientInterestSubmissions.objects.all().order_by("-date_submitted")
    context_object_name = "submissions"
    paginate_by = 25
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unresponsed"] = ClientInterestSubmissions.objects.filter(reviewed=False).count()
        context["showSearch"] = True
        context["reviewed"] = ClientInterestSubmissions.objects.filter(
        reviewed=True,
    ).count()
        context["all_submuission"] = ClientInterestSubmissions.objects.all().count()
        return context
        
class ClientInquiriesDetailView(DetailView):
    template_name = "home/submission-details.html"
    model = ClientInterestSubmissions
    context_object_name = "submission"
    pk_url_kwarg = "pk"

def marked_reviewed(request):
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


@login_required(login_url="/login/")
def employment_applications(request):
    context = dict()
    context["submissions"] = EmploymentApplicationModel.objects.all().order_by(
        "-date_submitted",
    )
    countUnresponsed = EmploymentApplicationModel.objects.filter(reviewed=False).count()
    context["unresponsed"] = countUnresponsed
    context["showSearch"] = True
    context["reviewed"] = EmploymentApplicationModel.objects.filter(
        reviewed=True,
    ).count()
    context["all_submuission"] = EmploymentApplicationModel.objects.all().count
    return render(request, "home/submitted-applications.html", context)


@login_required(login_url="/login/")
def applicant_details(request, pk):
    if request.user.is_staff:
        context = dict()
        submission = EmploymentApplicationModel.objects.get(pk=pk)
        context["type"] = "Client Interest"
        init_values = {
            "id": submission.id,
            "first_name": submission.first_name,
            "last_name": submission.last_name,
            "contact_number": submission.contact_number,
            "email": submission.email,
            "home_address1": submission.home_address1,
            "home_address2": submission.home_address2,
            "city": submission.city,
            "state": submission.state,
            "zipcode": submission.zipcode,
            "mobility": submission.mobility,
            "prior_experience": submission.prior_experience,
            "ipdh_registered": submission.ipdh_registered,
            "availability_monday": submission.availability_monday,
            "availability_tuesday": submission.availability_tuesday,
            "availability_wednesday": submission.availability_wednesday,
            "availability_thursday": submission.availability_thursday,
            "availability_friday": submission.availability_friday,
            "availability_saturday": submission.availability_saturday,
            "availability_sunday": submission.availability_sunday,
            "reviewed": submission.reviewed,
            "hired": submission.hired,
            "reviewed_by": submission.reviewed_by,
            "date_submitted": submission.date_submitted,
        }
        context["submission"] = init_values

        return render(request, "home/applicant-details.html", context)
    else:
        raise PermissionDenied()


@login_required(login_url="/login/")
def all_applicants(request) -> HttpResponse:
    inquiries = EmploymentApplicationModel.objects.all().values()
    for inquiry in inquiries:
        inquiry["contact_number"] = str(inquiry["contact_number"])
    applicant_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=applicant_json, status=200)


@login_required(login_url="/login/")
def coming_soon(request):
    return render(request, "coming_soon.html", {})
