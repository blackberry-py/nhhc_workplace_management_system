from datetime import datetime

from authentication.models import UserProfile
from compliance.models import Compliance, Contract
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from employee.models import Employee
from portal.models import Exception  # Assessment, InServiceTraining,
from web.models import ClientInterestSubmissions, EmploymentApplicationModel

now = datetime.now()
# Register your models here.
all_models = [
    Contract,
    Exception,
    Compliance,
    ClientInterestSubmissions,
    EmploymentApplicationModel,
    UserProfile,
]


class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ["username", "first_name", "last_name", "social_security", "phone"]
    list_display = ["first_name", "last_name", "username", "hire_date"]
    actions = []
    date_hierarchy = "hire_date"

    # SECTION - Custom Admin Actions
    @admin.action(description="Rehire selected Employee Groups")
    def rehire(self, request: HttpRequest, queryset: QuerySet[Employee]) -> None:
        """
        Reactivates the profield for the selected employees as published via Admin Site.

        Args:
            self: The instance of the class.
            request: The HTTP request object.
            queryset: The queryset of posts to be marked as published.

        Returns:
            None

        Raises:
            None
        """
        if queryset.exists():
            updated = queryset.update(
                is_active=True, termination_date=None, hire_date=now()
            )
            self.message_user(
                request,
                ngettext(
                    "%d post was successfully marked as published.",
                    "%d posts were successfully marked as published.",
                    updated,
                )
                % updated,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "No posts were selected.", messages.WARNING)


for model in all_models:
    admin.site.register(model)

admin.site.register(Employee, EmployeeAdmin)
