from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("announcements", views.AnnoucementsListView.as_view(), name="announcements"),
    path(
        "announcement/draft/",
        csrf_exempt(views.save_announcement),
        name="draft-announcement",
    ),
    path("announcement/create/", csrf_exempt(views.post_announcement), name="create-annoucement"),
    path("announcement/archive/", views.delete_announcement, name="archive-annoucement"),
    path("announcement/<int:pk>/", views.AnnoucementsUpdateView.as_view(), name="announcement_detail"),
]
