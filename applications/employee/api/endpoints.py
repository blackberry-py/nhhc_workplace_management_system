from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from applications.employee.api.serializers import EmployeeSerializer
from applications.employee.models import Employee

# Serializers define the API representation.


# ViewSets define the view behavior.
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeRosterAPIView(ListCreateAPIView):
    """
    REST API endpoint for managing the list and creation of Employee objects.

    Attributes:
    queryset (QuerySet): A queryset of all Employee objects.
    serializer_class (tuple): A tuple containing the serializer class for Employee objects.
    permission_classes (list): A list of permission classes required for accessing this view.
    filter_backends (list): A list of filter backends used for filtering Employee objects.
    filterset_fields (list): A list of fields that can be used for filtering Employee objects.

    """

    queryset = Employee.objects.all()
    serializer_class = (EmployeeSerializer,)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "is_active",
        "is_superuser",
        "gender",
        "language",
        "marital_status",
        "ethnicity",
        "race",
        "city",
        "state",
        "ethnicity",
        "zipcode",
        "qualifications",
        "in_compliance",
        "onboarded",
    ]
