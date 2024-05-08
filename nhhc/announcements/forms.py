"""
Module: annoucements.forms

This module defines the AnnouncementForm class, which is a form used to create new announcements in the system.

The AnnouncementForm class is a subclass of the Django ModelForm class and is associated with the Announcements model. It includes fields for the message, announcement title, and message type.

Attributes:
    model (Announcements): The model associated with the form.
    fields (tuple): The fields to be included in the form.

Methods:
    __init__: Initializes the form with the necessary attributes and layout using the FormHelper class from crispy_forms.


This module provides a convenient way to create and customize announcement forms in Django applications.
"""

from announcements.models import Announcements
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Row, Submit, Layout, HTML
from django import forms
from tinymce.widgets import TinyMCE
from django.utils.translation import gettext_lazy as _
from formset.widgets import Selectize


class AnnouncementDetailsForm(forms.ModelForm):
    """
    A form for displaying and updating announcement details.

    This form allows users to view and edit the details of an announcement, burt also view the metadata such as posting date, posted by,

    Attributes:
        model (Model): The model associated with the form (Announcements).
        fields (str): The fields to include in the form (all fields).
        widgets (dict): Custom widgets for specific form fields.
    """

    class Meta:
        model = Announcements
        fields = ("message", "announcement_title", "message_type", "posted_by")
        widgets = {"message": TinyMCE(content_language="en", attrs={"col": 5, "rows": 5}), "message_type": Selectize}
        labels = {
            "message_type": _(
                "Type",
            ),
            "announcement_title": _(
                "Title",
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = "/"
        self.helper.form_id = "announcement-form"
        self.helper.form_method = "post"
        self.fields["message"].label = False

        self.helper.layout = Layout(
                Row(
                    HTML(
                        """
                <div class="form-group col-4 mb-0">
            <label class="form-label">Post Status</label>
            <h5 class="textinput form-control" readonly>{{ announcement.get_status_display }}</h5>
            </div>
                            """
                    ),
                    Column(
                        "announcement_title",
                        css_class="form-group col-lg-6 mb-0 editable ",
                        css_id="announcement_title",
                    ),
                    Column(
                        "message_type",
                        css_class="form-group col-lg-4 mb-0 editable ",
                        css_id="message_type",
                    ), css_class="form-row "
                ),
                Row(
                    Column(
                        "message",
                        css_class="form-group col-12 mb-0 editable form-text-area",
                        css_id="message",
                    ),css_class="form-row "
                ),
                HTML(
                    """
<hr class="uk-divider-icon"/>
                    <h4> Post Details</h4>
                    """
                ),
                Row(
                    HTML(
                        """
                <div class="form-group col-6 mb-0">
            <label class="form-label">Posted By</label>
            <h5 class="textinput form-control" readonly>{{ announcement.posted_by.username }}</h5>
            </div>
                            """
                    ),
                    HTML(
                        """
                <div class="form-group col-6 mb-0">
            <label class="form-label">Posted on</label>
            <h5 class="textinput form-control" readonly>{{ announcement.date_posted }}</h5>
            </div>
                            """
                    ),css_class="form-row "
                ),
                Row(
                        Submit("submit", "Update Announcement"),
                
                    HTML(""" <a href="{% url 'announcements' %}" class="btn btn-dark">Cancel</a>"""),
                    HTML("""
                         <button class="btn btn-danger" onClick="confirmPostArchival({{ announcement.pk }})">Archive Annoucement</button>
                         """
                    ),css_class="uk-text-right uk-modal-footer"
            
            )
        )


class AnnouncementForm(forms.ModelForm):
    """
    This class represents a form for creating new announcements.

    Attributes:
        model (Announcements): The model associated with the form.
        fields (tuple): The fields to be included in the form.
    """

    class Meta:
        """ """

        model = Announcements
        fields = ("message", "announcement_title", "message_type")
        widgets = {"message": TinyMCE(content_language="en", attrs={"col": 5, "rows": 5}), "message_type": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = "/"
        self.helper.form_id = "announcement-form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(
                    "announcement_title",
                    css_class="form-group col-lg-8 mb-0 editable ",
                    css_id="announcement_title",
                ),
                Column(
                    "message_type",
                    css_class="form-group col-lg-4 mb-0 editable ",
                    css_id="message_type",
                ),
                css_class="form-row ",
            ),
            Row(
                Column(
                    "message",
                    css_class="form-group col-12 mb-0 editable form-text-area",
                    css_id="message",
                ),
                css_class="form-row ",
            ),
            Row(
                FormActions(
                    Submit(
                        "submit",
                        "Post Announcement",
                        onClick="confirmAnnouncementPost",
                    ),
                    Button("cancel", "Cancel", css_class="btn btn-danger uk-modal-close"),
                    Button(
                        "submit",
                        "Save Draft",
                        css_class="btn btn-danger",
                        onClick="",
                    ),
                ),
                css_class="uk-text-right uk-modal-footer",
            ),
        )
