from announcements.models import Announcements
from crispy_forms.bootstrap import FormActions
from crispy_forms.bootstrap import Modal
from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Reset
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
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
                        "message_type",
                        css_class="form-group col-lg-4 mb-0 editable ",
                        css_id="message_type",
                    ),
                ),
                Row(
                    Column(
                        Column(
                            "message",
                            css_class="form-group col-lg-4 mb-0 editable form-text-area",
                            css_id="message",
                        ),
                    ),
                ),
            ),
        )
