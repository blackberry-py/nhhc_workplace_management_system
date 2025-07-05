from typing import Any, Dict, Union

from celery import shared_task
from loguru import logger

from applications.web.forms import ClientInterestSubmission, EmploymentApplicationForm
from common.errors import ElectronicMailTransmissionError
from common.mailer import PostOffice

career_web_mailer = PostOffice()


def process(form, type):
    status = {"internal_notification": False, "external_confirmation": False, "error": None}

    if type == "Application":
        try:

            try:
                career_web_mailer.send_internal_new_applicant_notification(form)
                status["internal_notification"] = True
                logger.debug("Successfully Sent Internal Notification Email")
            except ElectronicMailTransmissionError as e:
                logger.error(f"Failed to send internal notification: {e}")
                status["error"] = f"Internal notification failed: {str(e)}"

            try:
                career_web_mailer.send_external_application_submission_confirmation(form)
                status["external_confirmation"] = True
                logger.debug("Successfully Sent External Confirmation Email")
            except ElectronicMailTransmissionError as e:
                logger.error(f"Failed to send external confirmation: {e}")
                status["error"] = f"External confirmation failed: {str(e)}"

            return status

        except Exception as e:
            return catch_general_exception(e, status)
    elif type == "clientRequest":
        try:
            try:
                career_web_mailer.send_internal_new_client_service_request_notification(form)
                status["internal_notification"] = True
                logger.debug("Successfully Sent Internal Notification Email")
            except ElectronicMailTransmissionError as e:
                logger.error(f"Failed to send internal notification: {e}")
                status["error"] = f"Internal notification failed: {str(e)}"

            try:
                career_web_mailer.send_external_client_submission_confirmation(form)
                status["external_confirmation"] = True
                logger.debug("Successfully Sent External Confirmation Email")
            except ElectronicMailTransmissionError as e:
                logger.error(f"Failed to send external confirmation: {e}")
                status["error"] = f"External confirmation failed: {str(e)}"

            return status
        except Exception as e:
            return catch_general_exception(e, status)


# TODO Rename this here and in `process`
def catch_general_exception(e, status):
    logger.error(f"UNABLE TO SEND: {e}")
    status["error"] = f"Unexpected error: {str(e)}"
    return status


@shared_task(bind=True)
def process_new_application(self, form: Union[EmploymentApplicationForm, Dict[str, Any]], **kwargs) -> Dict[str, bool]:
    """
    Async Celery task to Process new employment interest by sending internal and external notifications.

    Args:
        form (Union[EmploymentApplicationForm,Dict[str,Any]]): The form submitted by the client.

    Returns:
        Dict[str,int]: A dictionary containing the results of the notification t1sks. The values represent the number of notifications successful sent.
    """
    # try:
    #     logger.info(f"Processing New Application - Sending EMAILS: Celery Task id {self.request.id}, args: {self.request.args!r} kwargs: {self.request.kwargs!r}")
    #     career_web_mailer.send_internal_new_applicant_notification(form)
    #     logger.debug("Successfully Sent Internal Notification Email")
    #     career_web_mailer.send_external_application_submission_confirmation(form)
    return process(form, "Application")


@shared_task(bind=True)
def process_new_client_interest(self, form: Union[ClientInterestSubmission, Dict[str, Any]], **kwargs) -> Dict[str, bool]:
    """
    Async Celery task to Process new client interest by sending internal and external notifications.

    Args:
        form (Union[ClientInterestSubmission,Dict[str,Any]]): The form submitted by the client.

    Returns:
        Dict[str,int]: A dictionary containing the results of the notification tasks. The values represent the number of notifications successful sent.
    """
    return process(form, "clientRequest")
