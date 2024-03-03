from loguru import logger
from employee.models import Employee
from django.db.models import signals


def employee_terminated_signal(sender, instance, **kwargs) -> None:
    try:
        employee = Employee.objects.get(username=instance.username)
        if not employee.is_active and employee.termination_date is not None:
            logger.info(
                f"Archiving Terminated Employee - {employee.last_name}, {employee.first_name}"
            )
            # TODO: Complete Stroage Set up AND then implement profile archival
    except Employee.DoesNotExist:
        pass


signals.pre_save.connect(
    employee_terminated_signal, sender=Employee, dispatch_uid="employee.models"
)


signals.pre_save.connect(
    password_change_signal,
    sender=Employee,
    dispatch_uid=f"employee.models + {str(uuid4())}",
)

signals.post_save.connect(
    create_user_profile_signal,
    sender=Employee,
    dispatch_uid=f"employee.models + {str(uuid4())}",
)
