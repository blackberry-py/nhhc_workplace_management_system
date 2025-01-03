"""
Module: compliance.urls.py

This module defines the URL patterns for the compliance application in Django. It includes paths for various compliance-related views such as profile details, form submissions, and document signing.

URL Patterns:
- /compliance/ : Displays the Compliance Profile Detail View.
- /staff_compliance/<int:pk> : Allows staff members to update compliance information.
- /sign/hca : Handles signing of HCA compliance documents.
- /sign/idoa : Handles signing of IDOA compliance documents.
- /sign/dnd : Handles signing of Do Not Drive compliance documents.
- /sign/jobdesc : Handles signing of Job Description compliance documents.
- /sign/dhs/i9 : Handles signing of DHS I9 compliance documents.
- /sign/irs/w4 : Handles signing of IRS W4 compliance documents.
- /sign/il/w4 : Handles signing of IL W4 compliance documents.
- /sign/idph/bg-auth : Handles signing of IDPH Background Authorization compliance documents.
- /updated/ : Displays a success message after a form update.
- /signed/ : Processes signed attestations using AWS Lambda and stores them in S3.

Note: The 'csrf_exempt' decorator is used for certain views to exempt them from CSRF verification.
"""

from compliance import views
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    re_path(r"^compliance/$", views.ComplianceProfileDetailView.as_view(), name="compliance-profile"),
    path("staff_compliance/<int:pk>", csrf_exempt(views.ComplianceProfileFormView.as_view()), name="staff_update_compliance"),
    path("sign/hca", views.DocusealCompliaceDocsSigning_HCA.as_view(), name="hca_sign"),
    path("sign/idoa", views.DocusealCompliaceDocsSigning_IDOA.as_view(), name="idoa_sign"),
    path("sign/dnd", views.DocusealCompliaceDocsSigning_DoNotDrive.as_view(), name="dnd_sign"),
    path("sign/jobdesc", views.DocusealCompliaceDocsSigning_JobDesc.as_view(), name="jobdesc_sign"),
    path("sign/dhs/i9", views.DocusealCompliaceDocsSigning_i9.as_view(), name="i9_sign"),
    path("sign/irs/w4", views.DocusealCompliaceDocsSigning_irs_w4.as_view(), name="w4_sign"),
    path("sign/il/w4", views.DocusealCompliaceDocsSigning_il_w4.as_view(), name="il_w4_sign"),
    path("sign/idph/bg-auth", views.DocusealCompliaceDocsSigning_idph_bg_auth.as_view(), name="bg_sign"),
    path("updated/", views.SuccessfulUpdate.as_view(), name="form-updated"),
    re_path(
        r"^signed/$", csrf_exempt(views.signed_attestations), name="signed_form_processing"
    ),  # NOTE - Using AWS Lambda to decoupled to process signed forms from Docseal Webhook, and Post the signed form to s3
]
