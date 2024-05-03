from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from web.forms import ClientSubmissionForm, EmploymentApplicationForm
from nhhc.utils.email_templates import APPLICATION_BODY, CLIENT_BODY, PLAIN_TEXT_CLIENT_BODY, PLAIN_TEXT_APPLICATION_BODY
import smtplib 
# from django.http import HttpRequest
# import resend
# from django.utils.html import escape, format_html
# from django.utils.safestring import SafeText, mark_safe

redis = get_redis_connection('')
# RESEND_API_KEY = settings.RESEND_API_KEY

class PostOffice(EmailMultiAlternatives):
    def __init__(self): 
        self,
        from_email=settings.EMAIL,
        connection=None,
        attachments=None,
        headers=None,
        cc=None,
        reply_to=settings.EMAIL
        
    @classmethod
    def send_external_application_submission_confirmation(cls,form:EmploymentApplicationForm ):
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
            subject: str = f"Thanks For Your Employment Interest, {form.cleaned_data['first_name']}!"
            to: str = form.cleaned_data["email"].lower() 
            content_subtype = 'html'
            html_message = APPLICATION_BODY
            text_content = PLAIN_TEXT_APPLICATION_BODY
            
            msg = EmailMultiAlternatives(subject=subject, to=[to], text_content=text_content)
            msg.attach_alternative(html_content, "text/html")
        except Exception as e:
            logger.error(f'ERROR: Unable to Send Email - {e}')            