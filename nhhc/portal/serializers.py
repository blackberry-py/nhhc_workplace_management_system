from rest_framework.serializers import ModelSerializer, Serializer
from web.models import ClientInterestSubmissions, EmploymentApplicationModel


class ClientInquiriesSerializer(ModelSerializer):
    class Meta:
        model = ClientInterestSubmissions
        fields = "__all__"


class EmploymentApplicationSerializer(ModelSerializer):
    class Meta:
        model = EmploymentApplicationModel
        fields = "__all__"
