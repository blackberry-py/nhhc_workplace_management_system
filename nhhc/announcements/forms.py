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
from crispy_forms.bootstrap import FormActions, Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Row, Submit
from django import forms


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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = "/"
        self.helper.form_id = "announcement-form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Modal(
                Row(
                    Column(
                        "announcement_title",
                        css_class="form-group col-lg-8 mb-0 editable ",
                        css_id="announcement_title",
                    ),
                    Column(
                        InlineRadios("message_type"),
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
                        Button("cancel", "Cancel", css_class="btn btn-danger"),
                        Button(
                            "submit",
                            "Save Draft",
                            css_class="btn btn-danger",
                            onClick="confirmAnnouncementDraft",
                        ),
                    )
                ),
                css_id="new-annoucement-modal",
                title="Create New Announcement",
                title_class="w-100 text-center",
            ),
        )
