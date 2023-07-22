import csv
import json
import os

import pendulum
from announcements.forms import AnnouncementForm
from announcements.models import Announcements
from compliance.models import Compliance
from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import reverse
from django.template import loader
from django.urls import reverse
from django.views.generic.detail import DetailView
from employee.forms import EmployeeForm
from employee.models import Employee
from icecream import ic
from web.forms import ClientInterestForm
from web.models import ClientInterestSubmissions
from web.models import EmploymentApplicationModel

now = pendulum.now(tz="America/Chicago")


@login_required(login_url="/login/")
def index(request):
    context = dict()
    context["segment"] = "index"
    announcements = Announcements.objects.all().order_by("-date_posted")[:10]
    context["announcements"] = announcements
    html_template = loader.get_template("home/index.html")
    return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
# def pages(request):
#     context = {}
#     ic(context)
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:
#         load_template = request.path.split("/")[-1]

#         if load_template == "admin":
#             return HttpResponseRedirect(reverse("admin:index"))
#         context["segment"] = load_template

#         html_template = loader.get_template("home/" + load_template)
#         return HttpResponse(html_template.render(context, request))

#     except template.TemplateDoesNotExist:
#         html_template = loader.get_template("home/page-404.html")
#         return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def profile(request):
    context = dict()
    context["data"] = Employee.objects.get(id=request.user.id)
    context["compliance"] = Compliance.objects.get(employee_id=request.user.id)
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


@login_required(login_url="/login/")
def client_inquiries(request):
    context = dict()
    context["submissions"] = ClientInterestSubmissions.objects.all().order_by(
        "-date_submitted",
    )
    countUnresponsed = ClientInterestSubmissions.objects.filter(reviewed=False).count()
    context["unresponsed"] = countUnresponsed
    context["showSearch"] = True
    context["reviewed"] = ClientInterestSubmissions.objects.filter(
        reviewed=True,
    ).count()
    context["all_submuission"] = ClientInterestSubmissions.objects.all().count
    return render(request, "home/service-inquiries.html", context)


@login_required(login_url="/login/")
def submission_detail(request, pk):
    context = dict()
    submission = ClientInterestSubmissions.objects.get(pk=pk)
    context["type"] = "Client Interest"
    init_values = {
        "id": submission.id,
        "first_name": submission.first_name,
        "last_name": submission.last_name,
        "email": submission.email,
        "contact_number": submission.contact_number,
        "zipcode": submission.zipcode,
        "insurance_carrier": submission.insurance_carrier,
        "desired_service": submission.desired_service,
        "date_submitted": submission.date_submitted,
        "reviewed": submission.reviewed,
        "reviewed_by": submission.reviewed_by,
    }
    context["submission"] = init_values

    return render(request, "home/submission-details.html", context)


def marked_reviewed(request):
    try:
        body_unicode = request.data.decode("utf-8")
        body = json.loads(body_unicode)
        pk = body["pk"]
        submission = ClientInterestSubmissions.objects.get(id=pk)
        submission.marked_reviewed(request.user)
        submission.save()
        return HttpResponse(status=204)
    except Exception as e:
        ic(e)
        return HttpResponse(status=418)


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
            "home_address": submission.home_address,
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


def all_applicants(request):
    inquiries = EmploymentApplicationModel.objects.all().values()
    applicant_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=applicant_json, status=200)
