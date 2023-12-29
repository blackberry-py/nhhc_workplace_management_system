from django.urls import path

from . import views

urlpatterns = [
    path("announcements", views.announcements, name="announcements"),
    path(
        "create-announcement-draft",
        views.save_announcement,
        name="create-announcement",
    ),
]
