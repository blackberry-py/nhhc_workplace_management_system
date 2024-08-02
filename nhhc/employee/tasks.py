from celery import shared_task
from celery.utils.log import get_task_logger
from loguru import logger

from nhhc.utils.helpers import exponentially_retry
from nhhc.utils.mailer import PostOffice

celery_logger = get_task_logger(__name__)

hr_mailroom = PostOffice("HR@netthandshome.care")


def send_async_onboarding_email(applicant: dict) -> int:
    try:
        task = hr_mailroom.send_external_applicant_new_hire_onboarding_email(new_hire=applicant)
        logger.info("sending Onboarding Email")
        return task
    except Exception as e:
        logger.error(f"Async Onboarding Email Failed: {e}")


def send_async_rejection_email(applicant: dict) -> int:
    try:
        task = hr_mailroom.send_external_applicant_rejection_email(rejected_applicant=applicant)
        logger.info("sending Applicant Rejection")
        return task
    except Exception as e:
        logger.error(f"Async Rejection Email Failed - {e}")


def send_async_temrination_email(applicant: dict) -> int:
    try:
        task = hr_mailroom.send_external_applicant_termination_email(terminated_employee=applicant)
        logger.info("sending Applicant Rejection")
        return task
    except Exception as e:
        logger.error(f"Async Rejection Email Failed - {e}")
