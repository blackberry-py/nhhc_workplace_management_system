import json
from typing import Dict

from announcements.forms import AnnouncementForm, AnnouncementDetailsForm
from announcements.models import Announcements
from django.http import HttpRequest, HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin
from formset.views import FormView
from django.views import View
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.forms.models import model_to_dict

# Create your views here.


def app_status(request: HttpRequest) -> HttpResponse:
    """Return the status of the application."""
    # TODO: Imple=ment App Specific Heartbeart
    pass


class AnnoucementsListView(FormMixin, ListView):
    model = Announcements
    queryset = Announcements.objects.all().order_by("-date_posted")
    template_name = "annoucements.html"
    context_object_name = "announcement"
    success_url = "/announcements"
    form_class = AnnouncementForm
    paginate_by = 25
    extra_context = {
        "modal_title": "Create New Annoucement"
    }

class AnnoucementsUpdateView(UpdateView):
    form_class = AnnouncementDetailsForm
    model = Announcements
    template_name = "annoucements-details.html"

    def get_success_url(self) -> str:
        obj = model_to_dict(self.get_object())
        obj_id = obj["id"]
        return reverse('announcement_detail', pk = obj_id)
    
  


class AnnouncementFormView(FormView):
    form_class = AnnouncementForm
    model = Announcements
    template_name = "new_.html"
    success_url = "/announcements"



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
