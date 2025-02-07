from rest_framework.serializers import HyperlinkedModelSerializer

from applications.employee.models import Employee


class EmployeeSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
