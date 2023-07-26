from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt


from . import views

urlpatterns = [
    path("", csrf_exempt(views.index), name="index"),
    path("about/", views.about, name="about"),
    path("client-interest/", views.client_interest, name="client-interest"),
    path("employment-application/", views.employee_interest, name="application"),
    path("submission-confirmation/", views.submitted, name="submitted"),
    re_path(r"^robots.txt/$", csrf_exempt(views.robots_txt)), 
]
