"""
module: nhhc.signals

The module `signal_handlers.py` contains signal handler functions that are designed to respond to specific events or triggers within the application. These signal handlers are connected to various Django model signals to execute custom logic when certain actions occur.

Signal Handlers:
    - create_ancillary_profiles_signal
    - password_change_signal
    - employee_terminated_signal

"""

from typing import Callable
from uuid import uuid4

from authentication.models import UserProfile
from compliance.models import Compliance
from django.db.models import signals
from employee.models import Employee
from loguru import logger
from web.models import EmploymentApplicationModel
from nhhc.utils.mailer import PostOffice
from django.forms.models import model_to_dict
# SECTION - Communication Related Signals

def email_application_confirmation_external(sender: Callable, instance, created, **kwargs) -> None:
    if created:
        applicant=model_to_dict(EmploymentApplicationModel.objects.get(pk=instance.pk))
        logger.info(f"Confirmation Email Sending Triggetred - Beginning Emailto {applicant['email']}")
        PostOffice.send_external_application_submission_confirmation(applicant)

# SECTION - User Management Signals
def create_ancillary_profiles_signal(sender: Callable, instance, created, **kwargs) -> None:
    """
    This function is a signal handler that creates ancillary profiles (User Profile and Compliance) for a user when a new user instance is created.

    Args:
        sender (Callable): The sender of the signal.
        instance: The instance of the user that triggered the signal.
        created: A boolean indicating if the user instance was created.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        None
    """
    if created:
        UserProfile.objects.create(user=instance)
        logger.debug(f"Signal Triggered for UserProfile Creation for {instance}")
        Compliance.objects.create(employee=instance)
        logger.debug(f"Signal Triggered for Compliance Creation for {instance}")


def password_change_signal(sender, instance, **kwargs) -> None:
    """
    The password_change_signal function is designed to handle password change signals for Employee instances. This function checks if the user's password has been updated and updates the force_password_change attribute in the user's profile accordingly.

    Args:
        sender: The model class that sent the signal.
        instance: The instance of the model that triggered the signal.
        kwargs: Additional keyword arguments.
    Returns:
        None
    """
    try:
        user = Employee.objects.get(username=instance.username)
        if not user.password == instance.password:
            profile = user.get_profile()
            profile.force_password_change = False
            profile.save()
    except Employee.DoesNotExist:
        pass


def employee_terminated_signal(sender, instance, **kwargs) -> None:
    """
    This function handles the signal for when an employee is terminated.

    Args:
        sender (object): The model class that sent the signal.
        instance (object): The instance of the model that triggered the signal.
        **kwargs: Additional keyword arguments.

    Returns:
        None

    Notes:
    - If the terminated employee is found in the database and is not active with a termination date,
      the function logs the archival process.
    """
    try:
        employee = Employee.objects.get(username=instance.username)
        if not employee.is_active and employee.termination_date is not None:
            logger.info(f"Archiving Terminated Employee - {employee.last_name}, {employee.first_name}")
            # TODO: Complete Stroage Set up AND then implement profile archival
    except Employee.DoesNotExist:
        pass


signals.pre_save.connect(employee_terminated_signal, sender=Employee, dispatch_uid="employee.models")


signals.pre_save.connect(
    password_change_signal,
    sender=Employee,
    dispatch_uid=f"employee.models + {str(uuid4())}",
)

signals.post_save.connect(
    create_ancillary_profiles_signal,
    sender=Employee,
    dispatch_uid=f"employee.models + {str(uuid4())}",
)
signals.post_save.connect(
    email_application_confirmation_external,
    sender=EmploymentApplicationModel,
    dispatch_uid=f"applicantion + {str(uuid4())}",
)
