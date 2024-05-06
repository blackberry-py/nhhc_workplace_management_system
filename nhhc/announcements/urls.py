from django.urls import path

from . import views

urlpatterns = [
    path("announcements", views.AnnoucementsListView.as_view(), name="announcements"),
    path(
        "create-announcement-draft",
        views.save_announcement,
        name="create-announcement",
    ),
    path("announcement/<int:pk>/", views.AnnoucementsUpdateView.as_view(), name="announcement_detail")
]
