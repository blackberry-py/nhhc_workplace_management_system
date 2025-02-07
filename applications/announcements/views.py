import json

from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormMixin, UpdateView
from django.views.generic.list import ListView
from formset.views import FormView
from loguru import logger

from applications.announcements.forms import AnnouncementDetailsForm, AnnouncementForm
from applications.announcements.models import Announcements

# Create your views here.


def app_status(request: HttpRequest) -> HttpResponse:
    """Return the status of the application."""
    # TODO: Implement App Specific Heartbeart


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
        new_announcement = Announcements.objects.get(id=pk)
        new_announcement.status = "A"
        new_announcement.save()
        return HttpResponse(status=204)


class AnnouncementsListView(FormMixin, ListView):
    model = Announcements
    queryset = Announcements.objects.all()
    template_name = "announcements/announcements.html"
    context_object_name = "announcements"
    success_url = "/announcements"
    form_class = AnnouncementForm
    paginate_by = 25
    extra_context = {"modal_title": "Create New Announcement", "sort_entity_selector": '".announcements"'}

    def post(self, request):
        return redirect(to=reverse("announcements:create-announcement"))


class AnnouncementsUpdateView(UpdateView):
    form_class = AnnouncementDetailsForm
    queryset = Announcements.objects.all()
    model = Announcements
    template_name = "Announcements.objects.all()-details.html"
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
def delete_announcement(request: HttpRequest) -> HttpResponse:
    pk = int(request.POST.get("pk"))
    logger.debug(pk)
    if pk is not None:
        archived_announcement = Announcements.objects.get(id=pk)
        archived_announcement.archive()
        return HttpResponse(status=204)
    else:
        logger.error("No Announcement Found")
        return HttpResponse(status=404)
