from announcements.models import Announcements
from crispy_forms.bootstrap import FormActions, InlineRadios, Modal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Column, Layout, Reset, Row, Submit
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcements
        fields = ("message", "announcement_title", "message_type")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = "/"
        self.helper.form_id = "announcement"
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
                    ),                 css_class="form-row "),
                Row(
                    Column(
                            "message",
                            css_class="form-group col-12 mb-0 editable form-text-area",
                            css_id="message",
                   ),
                                css_class="form-row "),
            Row(
                FormActions(
                    Button("submit", "Post Announcement", onClick="confirmAnnouncementPost"),
                    Button("cancel", "Cancel", css_class="btn btn-danger"),
                    Button("submit","Save Draft", css_class="btn btn-danger", onClick="confirmAnnouncementDraft")
                )
            ), 
        css_id="new-annoucement-modal",
        title="Create New Announcement",
        title_class="w-100 text-center",
            ),
        )
