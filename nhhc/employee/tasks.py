from celery import shared_task
from celery.utils.log import get_task_logger
from loguru import logger

from nhhc.utils.mailer import PostOffice

celery_logger = get_task_logger(__name__)

hr_mailroom = PostOffice("HR@netthandshome.care")


@shared_task
def send_async_onboarding_email(applicant: dict) -> int:
    """
    Sends an asynchronous onboarding email to a new hire.

    This function attempts to send an onboarding email to the specified applicant using the HR mailroom service.
    It logs the process and returns the task identifier if successful, or logs an error if the operation fails.

    Args:
        applicant (dict): A dictionary containing the new hire's information.

    Returns:
        int: The task identifier for the email sending operation.

    Raises:
        Exception: Logs an error if the email sending fails.
    """
    try:
        task = hr_mailroom.send_external_applicant_new_hire_onboarding_email(new_hire=applicant)
        logger.info("sending Onboarding Email")
        return task
    except Exception as e:
        logger.error(f"Async Onboarding Email Failed: {e}")


@shared_task
def send_async_rejection_email(applicant: dict) -> int:
    """
    Sends an asynchronous rejection email to an applicant.

    This function attempts to send a rejection email to the specified applicant using the HR mailroom service.
    It logs the process and returns the task identifier if successful, or logs an error if the operation fails.

    Args:
        applicant (dict): A dictionary containing the applicant's information.

    Returns:
        int: The task identifier for the email sending operation.

    Raises:
        Exception: Logs an error if the email sending fails.
    """
    try:
        task = hr_mailroom.send_external_applicant_rejection_email(rejected_applicant=applicant)
        logger.info("sending Applicant Rejection")
        return task
    except Exception as e:
        logger.error(f"Async Rejection Email Failed - {e}")


@shared_task
def send_async_termination_email(applicant: dict) -> int:
    """
    Sends an asynchronous termination email to a terminated employee.

    This function attempts to send a termination email to the specified applicant using the HR mailroom service.
    It logs the process and returns the task identifier if successful, or logs an error if the operation fails.

    Args:
        applicant (dict): A dictionary containing the terminated employee's information.

    Returns:
        int: The task identifier for the email sending operation.

    Raises:
        Exception: Logs an error if the email sending fails.
    """
    try:
        task = hr_mailroom.send_external_applicant_termination_email(terminated_employee=applicant)
        logger.info("sending Applicant Rejection")
        return task
    except Exception as e:
        logger.error(f"Async Rejection Email Failed - {e}")
