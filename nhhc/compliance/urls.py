from compliance import views
from django.urls import path, re_path

urlpatterns = [
    re_path(r"^compliance/$", views.ComplianceProfileDetailView.as_view(), name="compliance-profile"),
    path("staff_compliance/<int:pk>", views.ComplianceProfileFormView.as_view(), name="staff_update_compliance"),
    path("sign/hca", views.DocusealCompliaceDocsSigning_HCA.as_view(), name="hca_sign"),
    path("sign/idoa", views.DocusealCompliaceDocsSigning_IDOA.as_view(), name="idoa_sign"),
    path("sign/dnd", views.DocusealCompliaceDocsSigning_DoNotDrive.as_view(), name="dnd_sign"),
    path("sign/jobdesc", views.DocusealCompliaceDocsSigning_JobDesc.as_view(), name="jobdesc_sign"),
    path("sign/dhs/i9", views.DocusealCompliaceDocsSigning_i9.as_view(), name="i9_sign"),
    path("sign/irs/w4", views.DocusealCompliaceDocsSigning_irs_w4.as_view(), name="w4_sign"),
    path("sign/il/w4", views.DocusealCompliaceDocsSigning_il_w4.as_view(), name="il_w4_sign"),
    path("signed/", views.signed_attestations, name="signed_form_processing"),  # NOTE - Using AWS Lambda to decoupled to process signed forms from Docseal Webhook, and Post the signed form to s3
]
