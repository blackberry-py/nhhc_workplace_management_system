from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from web.models import EmploymentApplicationModel
from nhhc.utils.email_templates import APPLICATION_BODY, CLIENT_BODY, PLAIN_TEXT_CLIENT_BODY, PLAIN_TEXT_APPLICATION_BODY
from loguru import logger
from django.core import mail
from django.forms.models import model_to_dict


class PostOffice(EmailMultiAlternatives):
    def __init__(self):
        self,
        from_email = (settings.EMAIL,)
        connection = (None,)
        attachments = (None,)
        headers = (None,)
        cc = (None,)
        reply_to = settings.EMAIL

    @classmethod
    def send_external_application_submission_confirmation(cls, applicant: dict):
        """
        Sends a confirmation email for a new employment interest or client interest submission.

        Args:
            form (ClientInterestForm | EmploymentApplicationForm): The form containing the submitted information.

        Returns:
            None

        Raises:
            Exception: If the email transmission fails.
        """

        try:
            subject: str = f"Thanks For Your Employment Interest, {applicant['first_name']}!"
            to: str = applicant["email"].lower()
            content_subtype = "html"
            html_content = APPLICATION_BODY
            text_content = PLAIN_TEXT_APPLICATION_BODY

            msg = EmailMultiAlternatives(subject=subject, to=[to], from_email=settings.EMAIL, body=text_content)
            msg.attach_alternative(html_content, "text/html")
            sent_emails = msg.send()
            if sent_emails == 0:
                raise RuntimeError("Email Not Sents")
            else:
                logger.success(f"Email Sent to {to}")
        except Exception as e:
            logger.trace(f"ERROR: Unable to Send Email - {e}")
