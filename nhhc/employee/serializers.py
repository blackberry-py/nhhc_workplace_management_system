from compliance.models import Compliance
from employee.models import Employee
from rest_framework.serializers import ModelSerializer, Serializer


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
