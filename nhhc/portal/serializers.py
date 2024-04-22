from rest_framework.serializers import ModelSerializer, Serializer
from web.models import ClientInterestSubmissions, EmploymentApplicationModel


class ClientInquiriesSerializer(ModelSerializer):
    """
    Serializer for the ClientInterestSubmissions model.

    This serializer is used to serialize and deserialize instances of the EmploymentApplicationModel.

    Attributes:
        model (EmploymentApplicationModel): The model class that this serializer is associated with.
        fields (str): The fields to include in the serialized data. If set to "__all__", all fields will be included.
    """

    class Meta:
        model = ClientInterestSubmissions
        fields = "__all__"


class EmploymentApplicationSerializer(ModelSerializer):
    """
    Serializer for the EmploymentApplicationModel model.

    This serializer is used to serialize and deserialize instances of the EmploymentApplicationModel.

    Attributes:
        model (EmploymentApplicationModel): The model class that this serializer is associated with.
        fields (str): The fields to include in the serialized data. If set to "__all__", all fields will be included.
    """

    class Meta:
        model = EmploymentApplicationModel
        fields = "__all__"
