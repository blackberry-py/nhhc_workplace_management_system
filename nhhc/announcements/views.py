from announcements.forms import AnnouncementForm
from announcements.models import Announcements
from django.shortcuts import render

# Create your views here.


def announcements(request):
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
    return render(request, "home/annoucements.html", context)


def save_announcement(request):
    new_announcement = Announcements(request.POST)
    new_announcement.save()
    return HttpResponse(status=201)


def post_announcement():
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


def delete_announcement():
    body_unicode = request.data.decode("utf-8")
    body = json.loads(body_unicode)
    pk = body["pk"]
    new_announcement = Announcements.objects.get(id=pk)
    new_announcement.status = "X"
    return HttpResponse(status=204)
