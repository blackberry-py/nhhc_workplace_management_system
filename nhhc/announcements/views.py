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
from django.views.generic.edit import UpdateView, FormMixin
from django.forms.models import model_to_dict
from django.views.decorators.http import require_POST
from loguru import logger

# Create your views here.
ANNOUCEMENTS = Announcements.objects.select_related("posted_by")


def app_status(request: HttpRequest) -> HttpResponse:
    """Return the status of the application."""
    # TODO: Imple=ment App Specific Heartbeart
    pass


class AnnoucementsListView(FormMixin, ListView):
    model = Announcements
    queryset = ANNOUCEMENTS
    template_name = "annoucements.html"
    context_object_name = "announcements"
    success_url = "\announcments"
    form_class = AnnouncementForm
    paginate_by = 25
    extra_context = {"modal_title": "Create New Annoucement", "sort_entity_selector": '".annoucements"'}


class AnnoucementsUpdateView(UpdateView):
    form_class = AnnouncementDetailsForm
    queryset = ANNOUCEMENTS
    model = Announcements
    template_name = "annoucements-details.html"
    context_object_name = "announcement"
    extra_context = {}

    def get_success_url(self) -> str:
        obj = model_to_dict(self.get_object())
        obj_id = obj["id"]
        return reverse("announcement_detail", pk=obj_id)


class AnnouncementFormView(FormView):
    form_class = AnnouncementForm
    model = Announcements
    template_name = "new_.html"
    success_url = "/announcements"


@require_POST
def save_announcement(request: HttpRequest) -> HttpResponse:
    new_announcement = Announcements(request.POST)
    new_announcement.create_draft()
    return HttpResponse(status=201)


@require_POST
def post_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    body_unicode = request.data.decode("utf-8")
    body = json.loads(body_unicode)
    pk = body["pk"]
    if pk is None:
        new_announcement = Announcements(request.POST)
        new_announcement.post()
        return HttpResponse(status=201)

    else:
        new_announcement = Announcements.objects.queryset_from_cache().get(id=pk)
        new_announcement.status = "A"
        new_announcement.save()
        return HttpResponse(status=204)


@require_POST
def delete_announcement(request: HttpRequest) -> HttpResponse:
    pk = int(request.POST.get("pk"))
    logger.debug(pk)
    if pk is not None:
        archived_announcement = Announcements.objects.queryset_from_cache().get(id=pk)
        archived_announcement.archive()
        return HttpResponse(status=204)
    else:
        logger.error("No Annoiucement FOunbd")
        return HttpResponse(status=404)


# elif "announcement_title" in request.POST.keys():
#     form = AnnouncementDetailsForm(request.POST)
#     if form.is_valid():
#         archived_announcement = Announcements.objects.queryset_from_cache().get(pk=form.cleaned_data.get('id'))
#         archived_announcement.archive()
#         return HttpResponse(status=204)
