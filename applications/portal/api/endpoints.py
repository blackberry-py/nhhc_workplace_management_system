import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from loguru import logger
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from applications.employee.models import Employee
from applications.portal.api.serializers import ClientInquiriesSerializer
from applications.web.models import ClientInterestSubmission, EmploymentApplicationModel
from common.cache import CachedResponseMixin


class EmploymentApplicationModelAPIListView(CachedResponseMixin, mixins.DestroyModelMixin, generics.ListCreateAPIView):
    queryset = EmploymentApplicationModel.objects.all()
    serializer_class = [EmploymentApplicationModel]
    primary_model = EmploymentApplicationModel
    cache_model = [Employee, EmploymentApplicationModel]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "reviewed",
        "hired",
        "home_address2",
        "city",
        "state",
        "zipcode",
        "mobility",
        "prior_experience",
        "ipdh_registered",
        "availability_monday",
        "availability_tuesday",
        "availability_wednesday",
        "availability_thursday",
        "availability_friday",
        "availability_saturday",
        "availability_sunday",
        "reviewed",
        "hired",
        "reviewed_by",
        "date_submitted",
    ]

    def destroy(self, request, instance):
        if request.user.is_superuser is False:
            return Response(
                data="Only Managers can preform a delete operation",
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def all_client_inquiries(request: HttpRequest) -> HttpResponse:
    """
    Retrieves all client inquiries and returns them as JSON.

    Returns:
    - HttpResponse: JSON response containing all client inquiries
    """
    inquiries = ClientInterestSubmission.objects.all().values()
    inquiries_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=inquiries_json, status=status.HTTP_200_OK)


class ClientInquiriesAPIListView(CachedResponseMixin, generics.ListCreateAPIView):
    queryset = ClientInterestSubmission.objects.all()
    primary_model = ClientInterestSubmission
    cache_models = []
    serializer_class = ClientInquiriesSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    filter_backends = [DjangoFilterBackend]


# TODO: Implement REST endpoint with DRF
@login_required(login_url="/login/")
def all_applicants(request: HttpRequest) -> HttpResponse:
    """
    Retrieves all employment applications and returns them as JSON.

    Returns:
    - HttpResponse: JSON response containing all employment applications
    """
    inquiries = EmploymentApplicationModel.objects.all().values()
    for inquiry in inquiries:
        inquiry["contact_number"] = str(inquiry["contact_number"])
    applicant_json = json.dumps(list(inquiries), cls=DjangoJSONEncoder)
    return HttpResponse(content=applicant_json, status=200)


def marked_reviewed(request):
    """
    Marks a client inquiry as reviewed.

    Returns:
    - HttpResponse: Success or error response
    """
    try:
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        pk = body["pk"]
        submission = ClientInterestSubmission.objects.get(id=pk)
        submission.marked_reviewed(request.user)
        submission.save()
        logger.info(f"{submission.id} marked as reviewed")
        return HttpResponse(status=204)
    except json.decoder.JSONDecodeError:
        logger.error("Error decoding request data")
        return HttpResponse(status=400)
    except ObjectDoesNotExist:
        logger.error(f"Object with pk {pk} Does Not Exist, Unable to Mark Reviewed")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"ERROR: Unable to Mark {submission.id} REVIEWED: {e}")
        return HttpResponse(status=500)
