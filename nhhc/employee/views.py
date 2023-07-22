import csv
import json
import os

import pendulum
from announcements.forms import AnnouncementForm
from announcements.models import Announcements
from compliance.forms import ComplianceForm
from compliance.models import Compliance
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
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


# Create your views here.
def send_new_user_credentials(new_user):
    """Internal Non-Rendering View Function to send email notification of user namne and password"""
    try:
        email_from = settings.EMAIL_HOST_USER
        sender_email = os.getenv("NOTIFICATION_SENDER_EMAIL")
        recipient_email = new_user.email
        sender_password = os.getenv("EMAIL_ACCT_PASSWORD")
        subject = f"Welcome to Nett Hands - {new_user.first_name}!"
        content = f"Welcome to Nett Hands, Please Login Your New Employee Account at https://www.netthandshome.care/login/ and Complete Onboarding Information in the Personal Information Section:\n Username = {new_user.first_name} \n Password = \n {new_user.first_name} \n "
        send_mail(subject, content, email_from, recipient_email)
    except Exception as e:
        return f"Something went wrong...{e}"


def hire(request):
    try:
        body_unicode = request.data.decode("utf-8")
        body = json.loads(body_unicode)
        pk = body["pk"]
        submission = EmploymentApplicationModel.objects.get(pk=pk)
        submission.hire(request.user)
        send_new_user_credentials(submission)
        submission.save()
        return HttpResponse(status=201)
    except Exception as e:
        ic(e)
        return HttpResponse(status=418)


def reject(request):
    try:
        body_unicode = request.data.decode("utf-8")
        body = json.loads(body_unicode)
        pk = body["pk"]
        submission = EmploymentApplicationModel.objects.get(id=pk)
        submission.reject(request.user)
        submission.save()
        return HttpResponse(status=204)
    except Exception as e:
        return HttpResponse(status=418)


def employee_roster(request):
    context = dict()
    employees = Employee.objects.all().order_by("last_name")
    context["employees"] = employees
    context["showSearch"] = True
    return render(request, "home/employee-listing.html", context)


def employee_details(request, pk):
    if request.user.is_staff:
        context = dict()
        context["data"] = Employee.objects.get(id=pk)
        context["compliance"] = Compliance.objects.get(employee=pk)
        user = context["data"]
        compliance = context["compliance"]

        if request.method == "POST":
            user = Employee.objects.get(id=pk)
            compliance = Compliance.objects.get(employee=pk)
            form = EmployeeForm(
                request.POST,
                request.FILES,
                instance=Employee.objects.get(id=pk),
            )
            if form.has_changed:
                if form.is_valid:
                    form.save()
                    return redirect(reverse("profile"))

        elif request.method == "GET":
            context["compliance"] = Compliance.objects.get(employee=pk)
            context["form"] = EmployeeForm(instance=Employee.objects.get(id=pk))
            return render(
                request=request,
                template_name="home/employee-details.html",
                context=context,
            )
    else:
        raise PermissionDenied()
