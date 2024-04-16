from compliance import views
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [re_path(r"^compliance/$", views.ComplianceProfile.as_view(), name="compliance-profile")]
