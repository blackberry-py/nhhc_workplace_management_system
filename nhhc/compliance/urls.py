from compliance import views
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    re_path(r"^compliance/$", views.ComplianceProfileDetailView.as_view(), name="compliance-profile"),
    path("staff_compliance/<int:pk>", views.ComplianceProfileFormView.as_view(), name="staff_update_compliance"),
]
