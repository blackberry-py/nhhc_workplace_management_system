from typing import Any, Dict, Union

from celery import shared_task
from django.http import HttpRequest
from loguru import logger
from web.forms import ClientInterestSubmission, EmploymentApplicationForm

from nhhc.utils.mailer import PostOffice

career_web_mailer = PostOffice(
    from_email="Careers@NettHandsHome.care",
    reply_to=list(
        "Careers@NettHandsHome.care",
    ),
)


@shared_task()
def process_new_application(form: Union[EmploymentApplicationForm, Dict[str, Any]], **kwargs) -> Dict[str, int]:
    """
    Async Celery task to Process new employment interest by sending internal and external notifications.

    Args:
        form (Union[EmploymentApplicationForm,Dict[str,Any]]): The form submitted by the client.

    Returns:
        Dict[str,int]: A dictionary containing the results of the notification tasks. The values represent the number of notifications successful sent.
    """
    try:
        logger.debug("Processing New Application - Sending EMAILS")
        if internal_notify_task := career_web_mailer.send_internal_new_applicant_notification(form):
            logger.debug("Successfully Sent Internal Notification Email")
            if external_notify_task := career_web_mailer.send_external_application_submission_confirmation(form):
                return {"internal": internal_notify_task, "external": external_notify_task}
    except Exception as e:
        logger.error(f"UNABLE TO SEND: {e}")
        return {"internal": 0, "external": 0}


client_web_mailer = PostOffice(
    from_email="CareCoordination@NettHandsHome.care",
    reply_to=list(
        "CareCoordination@NettHandsHome.care",
    ),
)


@shared_task
def process_new_client_interest(form: Union[ClientInterestSubmission, Dict[str, Any]], **kwargs) -> Dict[str, int]:
    """
    Async Celery task to Process new client interest by sending internal and external notifications.

    Args:
        form (Union[ClientInterestSubmission,Dict[str,Any]]): The form submitted by the client.

    Returns:
        Dict[str,int]: A dictionary containing the results of the notification tasks. The values represent the number of notifications succesful sent.
    """
    try:
        logger.info("Starting Client Submission Processing")
        internal_notify_task = client_web_mailer.send_internal_new_applicant_notification(form)
        external_notify_task = client_web_mailer.send_external_client_submission_confirmation(form)
        results: Dict[str, int] = {"internal": internal_notify_task, "external": external_notify_task}
        return results
    except Exception as e:
        logger.error(f"Unable to Send Client Confirmation Email:{e}")
