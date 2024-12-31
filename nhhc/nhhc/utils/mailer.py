import os

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, mail_managers
from django.forms.models import model_to_dict
from loguru import logger
from web.models import ClientInterestSubmission, EmploymentApplicationModel
from tenacity import retry, stop_after_attempt, wait_exponential

    def __init__(self, from_email=settings.DEFAULT_FROM_EMAIL, reply_to=settings.DEFAULT_FROM_EMAIL):
        self.from_email = from_email
        self.reply_to = reply_to
        self.logger = logging.getLogger(__name__)
        super().__init__()


from nhhc.utils.email_templates import (
    APPLICATION_BODY,
    CLIENT_BODY,
    INTERNAL_APPLICATION_NOTIFICATION,
    INTERNAL_CLIENT_SERVICE_REQUEST_NOTIFICATION,
    NEW_HIRE_ONBOARDING_TEMPLATE_BODY,
    PLAIN_TEXT_APPLICATION_BODY,
    PLAIN_TEXT_CLIENT_BODY,
    PLAIN_TEXT_NEW_HIRE_ONBOARDING_EMAIL_TEMPLATE,
    PLAIN_TEXT_REJECTION_EMAIL_TEMPLATE,
    PLAIN_TEXT_TERMINATION_EMAIL_TEMPLATE,
    REJECTION_TEMPLATE_BODY,
)
class ElectronicMailTransmissionError(RuntimeError):
    pass

class PostOffice(EmailMultiAlternatives):
    connection = (None,)
    attachments = (None,)
    headers = (None,)
    cc = (None,)
    reply_to = settings.EMAIL_HOST_USER
    internal_distro_list = settings.MANAGERS

    def __init__(self, from_email=settings.DEFAULT_FROM_EMAIL, reply_to=settings.DEFAULT_FROM_EMAIL):
        self.from_email = from_email
        self.reply_to = reply_to
        super().__init__()
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_external_application_submission_confirmation(self, applicant: dict) -> bool:
        """
        Sends a confirmation email for a new employment interest or client interest submission.

        Args:
            form (ClientInterestForm | EmploymentApplicationForm): The form containing the submitted information.

        Returns:
            bool

        Raises:
            Exception: If the email transmission fails.
        """
        if not isinstance(applicant, dict):
            applicant = model_to_dict(applicant)
        try:
            return self._extracted_from_send_external_application_submission_confirmation_17(applicant)
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            settings.HIGHLIGHT_MONITORING.record_exception(f"ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During EMail Transmission:{e}') from e

    # TODO Rename this here and in `send_external_application_submission_confirmation`
    def _extracted_from_send_external_application_submission_confirmation_17(self, applicant):
        subject: str = f"Thanks For Your Employment Interest, {applicant['first_name']}!"
        to: list = applicant["email"].lower()
        content_subtype = "text/html"
        html_content = APPLICATION_BODY.substitute(first_name=applicant["first_name"])
        text_content = PLAIN_TEXT_APPLICATION_BODY.substitute(first_name=applicant["first_name"])

        msg = EmailMultiAlternatives(subject=subject, to=[to], body=text_content, from_email=self.from_email, reply_to=[self.reply_to])
        msg.attach_alternative(html_content, content_subtype)
        sent_emails: int = msg.send()
        if sent_emails <= 0:
            logger.error(f"EMAIL TRANSMISSION FAILURE - {sent_emails}")
            raise ElectronicMailTransmissionError("Email Not Sent")
        logger.info(f"Number of External Emails Sent:{sent_emails}")
        return True
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_external_client_submission_confirmation(self, interested_client: dict) -> None:
        """
        Sends a confirmation email for a new client interest submission.

        Args:
            interested_client (dict) Dictonary representation  of the Instance of thr Client Submission
        Returns:
            None

        Raises:
            Exception: If the email transmission fails.
        """
        if not isinstance(interested_client, dict):
            interested_client = model_to_dict(interested_client)
        try:
            subject: str = f"We Are On It, {interested_client['first_name']}!"
            to: list = interested_client["email"].lower()
            content_subtype = "text/html"
            html_content = CLIENT_BODY.substitute(first_name=interested_client["first_name"])
            text_content = PLAIN_TEXT_CLIENT_BODY.substitute(first_name=interested_client["first_name"])

            msg = EmailMultiAlternatives(subject=subject, to=[to], from_email=self.from_email, reply_to=[self.reply_to], body=text_content)
            msg.attach_alternative(html_content, content_subtype)
            sent_emails = msg.send()
            if sent_emails <= 0:
                logger.error(f"EMAIL TRANSMISSION FAILURE - {sent_emails}")
                raise ElectronicMailTransmissionError("Email Not Sents")
            return True
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            settings.HIGHLIGHT_MONITORING.record_exception(f"ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During EMail Transmission:{e}') from e
     
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_external_applicant_rejection_email(self, rejected_applicant: dict) -> int:
        """
        Sends email rerjecting the application for employment of the reciepent

        Args:
            new_applicant (dict) Dictonary representation  of the Instance of the submitted application
        Returns:
            None

        Raises:
            Exception: If the email transmission fails.
        """

        if not isinstance(rejected_applicant, dict):
            rejected_applicant = model_to_dict(rejected_applicant)
            logger.info(f"Inititating EMAIL Transmission - Rejection Email - Receipent {rejected_applicant['last_name'], rejected_applicant['first_name']}({rejected_applicant['email']})")

        try:
            subject: str = f"Thank You So Much For Considering Nett Hands, {rejected_applicant['first_name']}!"
            to: list = rejected_applicant["email"].lower()
            content_subtype = "text/html"
            html_content = REJECTION_TEMPLATE_BODY.substitute(first_name=rejected_applicant["first_name"])
            text_content = PLAIN_TEXT_REJECTION_EMAIL_TEMPLATE.substitute(first_name=rejected_applicant["first_name"])
            msg = EmailMultiAlternatives(subject=subject, to=[to], from_email=self.from_email, reply_to=self.reply_to, body=text_content)
            msg.attach_alternative(html_content, content_subtype)
            sent_emails = msg.send()
            if sent_emails <= 0:
                logger.error(f"EMAIL TRANSMISSION FAILURE - {sent_emails}")
                raise ElectronicMailTransmissionError("Email Not Sent")
            return sent_emails
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During EMail Transmission:{e}') from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_external_applicant_termination_email(self, terminated_employee: dict) -> int:
        """
        Sends email terminating  employment of the recipient

        Args:
            new_applicant (dict) Dictonary representation  of the Instance of the submitted application
        Returns:
            None

        Raises:
            Exception: If the email transmission fails.
        """

        if not isinstance(terminated_employee, dict):
            terminated_employee = model_to_dict(terminated_employee)
            logger.info(f"Initiating EMAIL Transmission - Termination Email - Recipient {terminated_employee['last_name'], terminated_employee['first_name']}({terminated_employee['email']})")

        try:
            subject: str = f"NOTICE: Termination of Employment from Nett Hands Home Care"
            to: list = terminated_employee["email"].lower()
            content_subtype = "text/html"
            text_content = PLAIN_TEXT_TERMINATION_EMAIL_TEMPLATE.substitute(first_name=terminated_employee["first_name"])
            msg = EmailMessage(subject=subject, to=[to], from_email=self.from_email, reply_to=self.reply_to, body=text_content)
            sent_emails = msg.send()
            if sent_emails <= 0:
                logger.error(f"EMAIL TRANSMISSION FAILURE - {sent_emails}")
                raise ElectronicMailTransmissionError("Email Not Sent")
            return sent_emails
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During EMail Transmission:{e}') from e
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_external_applicant_new_hire_onboarding_email(self, new_hire: dict) -> int:
        """
        Sends email informing the application of their Login Credentials and the start of their emoployment

        Args:
            interested_client (dict) Dictonary representation of the newly hired Applicant's employee model instance
        Returns:
            int

        Raises:
            Exception: If the email transmission fails.
        """
        if not isinstance(new_hire, dict):
            new_hire = model_to_dict(new_hire)
        try:
            subject: str = f"Welcome to Nett Hands, {new_hire['first_name']}!"
            to: list = new_hire["email"].lower()
            content_subtype = "text/html"
            html_content = NEW_HIRE_ONBOARDING_TEMPLATE_BODY.substitute(first_name=new_hire["first_name"], username=new_hire["username"], plaintext_password=new_hire["plaintext_temp_password"])
            text_content = PLAIN_TEXT_NEW_HIRE_ONBOARDING_EMAIL_TEMPLATE.substitute(
                first_name=new_hire["first_name"], username=new_hire["username"], plaintext_password=new_hire["plaintext_temp_password"]
            )
            msg = EmailMultiAlternatives(subject=subject, to=[to], from_email=self.from_email, reply_to=[self.reply_to], body=text_content)
            msg.attach_alternative(html_content, content_subtype)
            sent_emails = msg.send()
            if sent_emails <= 0:
                logger.error(f"EMAIL TRANSMISSION FAILURE - {sent_emails}")
                raise ElectronicMailTransmissionError("Email Not Sent")
            return sent_emails
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During Email Transmission:{e}') from e
    @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            reraise=True
        )
    def send_internal_new_applicant_notification(self, applicant: dict) -> bool:
        """
        Trigger Intrernal Notification of a New Application

        Args:
            interested_client (dict) Dictornary representation of the newly hired Applicant's employee model instance

        Returns:
            bool if emails successfully send


        Raises:
            Exception: If the email transmission fails.
        """
        if not isinstance(applicant, dict):
            applicant = model_to_dict(applicant)
        try:
            subject: str = f"NOTICE: New Application For Employment - {applicant['last_name']}, {applicant['first_name']}!"
            body = INTERNAL_APPLICATION_NOTIFICATION.substitute(
                first_name=applicant["first_name"],
                last_name=applicant["last_name"],
                email=applicant["email"],
                contact_number=applicant["contact_number"],
                home_address=applicant["home_address1"],
                city=applicant["city"],
                state=applicant["state"],
                zipcode=applicant["zipcode"],
                mobility=applicant["mobility"],
                prior_experience=applicant["prior_experience"],
                availability_monday=applicant["availability_monday"],
                availability_tuesday=applicant["availability_tuesday"],
                availability_wednesday=applicant["availability_wednesday"],
                availability_thursday=applicant["availability_thursday"],
                availability_friday=applicant["availability_friday"],
                availability_saturday=applicant["availability_saturday"],
                availability_sunday=applicant["availability_sunday"],
                url_slug=EmploymentApplicationModel.objects.filter(email=applicant["email"], zipcode=applicant["zipcode"]).order_by("-date_submitted")[0].__dict__["id"],
                resume_url=applicant["resume_cv"]
            )
            mail_managers(subject=subject, fail_silently=False, message=body)
            return True
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During EMail Transmission:{e}') from e
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_internal_new_client_service_request_notification(self, interested_client: dict) -> int:
        """
        Trigger Intrernal Notification of a New Application

        Args:
            interested_client (dict) Dictornary representation of the newly hired Applicant's employee model instance
        Returns:
            int Number of emails successfully send

        Raises:
            Exception: If the email transmission fails.
        """
        if not isinstance(interested_client, dict):
            interested_client = model_to_dict(interested_client)
        try:
            subject: str = f"NOTICE: New Client Service Request - {interested_client['last_name']}, {interested_client['first_name']}!"
            to: list = settings.INTERNAL_SUBMISSION_NOTIFICATION_EMAILS
            body = INTERNAL_CLIENT_SERVICE_REQUEST_NOTIFICATION.substitute(
                first_name=interested_client["first_name"],
                last_name=interested_client["last_name"],
                email=interested_client["email"],
                desired_service=interested_client["desired_service"],
                contact_number=interested_client["contact_number"],
                zipcode=interested_client["zipcode"],
                insurance_carrier=interested_client["insurance_carrier"],
                url_slug=ClientInterestSubmission.objects.filter(email=interested_client["email"], insurance_carrier=interested_client["insurance_carrier"], zipcode=interested_client["zipcode"])
                .order_by("-date_submitted")[0]
                .__dict__["id"],
            )
            mail_managers(subject=subject, fail_silently=False, message=body)
            return True
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
            settings.HIGHLIGHT_MONITORING.record_exception("ERROR: Unable to Send Email - {e}")
            raise ElectronicMailTransmissionError(f'Exception Raised During EMail Transmission:{e}') from e

