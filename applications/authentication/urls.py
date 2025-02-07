"""
Modeule: authentication.urls
This module contains the URL patterns for the authentication  application.


The URL patterns include:


These URL patterns are used to define the routing for the views in the application.

"""

from authentication.views import CustomLoginView
from django.urls import path

app_name = "authentication"
urlpatterns = [path("login/", CustomLoginView.as_view(), name="account_login")]
