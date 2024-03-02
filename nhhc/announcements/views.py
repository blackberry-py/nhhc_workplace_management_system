import json

from announcements.forms import AnnouncementForm
from announcements.models import Announcements
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from formset.views import FormView

# Create your views here.


class AnnoucementsListView(ListView):
    model = Announcements
    queryset = Announcements.objects.all().order_by("-date_posted")
    template_name = "annoucements.html"
    context_object_name = "anouncement"
    paginate_by = 25
    
class AnnouncementFormView(FormView):
    form_class = AnnouncementForm
    model = Announcements
    template_name = "new_.html"
    success_url = "/profile"

def announcements(request: HttpRequest) -> HttpResponse:
    context = dict()
    if request.user.is_staff:
        announcements = Announcements.objects.all().order_by("-date_posted")
    else:
        announcements = Announcements.objects.filter(status="A").order_by.order_by(
            "-date_posted",
        )
    context["announcements"] = announcements
    context["showSearch"] = True
    context["form"] = AnnouncementForm()
    return render(request, "annoucements.html", context)


def save_announcement(request: HttpRequest) -> HttpResponse:
    new_announcement = Announcements(request.POST)
    new_announcement.save()
    return HttpResponse(status=201)


def post_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    body_unicode = request.data.decode("utf-8")
    body = json.loads(body_unicode)
    pk = body["pk"]
    if pk is None:
        new_announcement = Announcements(request.POST)
        new_announcement.status = "A"
        new_announcement.save()
        return HttpResponse(status=201)

    else:
        new_announcement = Announcements.objects.get(id=pk)
        new_announcement.status = "A"
        new_announcement.save()
        return HttpResponse(status=204)


def delete_announcement(request: HttpRequest) -> HttpResponse:
    body_unicode = request.data.decode("utf-8")
    body = json.loads(body_unicode)
    pk = body["pk"]
    new_announcement = Announcements.objects.get(id=pk)
    new_announcement.status = "X"
    return HttpResponse(status=204)
