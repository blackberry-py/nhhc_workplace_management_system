from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from applications.announcements import views

app_name = "announcements"
urlpatterns = [
    path("announcements", views.AnnouncementsListView.as_view(), name="announcements"),
    path(
        "announcement/draft/",
        csrf_exempt(views.save_announcement),
        name="draft-announcement",
    ),
    path("announcement/create/", csrf_exempt(views.post_announcement), name="create-announcement"),
    path("announcement/archive/", views.delete_announcement, name="archive-announcement"),
    path("announcement/<int:pk>/", views.AnnouncementsUpdateView.as_view(), name="announcement_detail"),
]
