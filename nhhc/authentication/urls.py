"""
Modeule: authentication.urls
This module contains the URL patterns for the authentication  application.


The URL patterns include:


These URL patterns are used to define the routing for the views in the application.

"""
from django.urls import include, path, re_path
from authentication.views import CustomLoginView
urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="account_login")
]
