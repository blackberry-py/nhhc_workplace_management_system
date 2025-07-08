import datetime
from datetime import timedelta

from arrow import get, now
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Layout, Row, Submit
from django.forms import ModelForm, widgets
from django.forms.fields import BoundField, DateField, TimeField
from django.forms.fields import Field as FormsField
from formset.widgets import DatePicker

from applications.portal.models import PayrollException


def calculateExceptionHours(start: int, end: int) -> int:
    """
    Calculates the difference in hours between two time values.

    Args:
        start: The starting time value in the format '%H:%M:%S'.
        end: The ending time value in the format '%H:%M:%S'.

    Returns:
        int: The difference in hours between the two time values.

    """
    start_time = datetime.strptime(start, "%H:%M:%S")
    end_time = datetime.strptime(end, "%H:%M:%S")
    time_delta = end_time - start_time
    return divmod(time_delta.total_seconds(), 3600)[0]


class HoursExceptionBoundField(BoundField):
    @property
    def hours(self, start_time, end_time):
        self.start_time = datetime.strptime(start_time, "%H:%M:%S")
        self.end_time = datetime.strptime(end_time, "%H:%M:%S")
        timedelta = self.end_time - self.start_time
        24 * 60 * 60
        return divmod(timedelta.total_seconds(), 3600)[0]


class HoursExceptionField(FormsField):
    def __init__(self, label, initial, start_time, end_time, required=False, widget=widgets.NumberInput, help_text=""):
        self.required = required
        self.label = label
        self.initial = initial
        self.widget = widget
        self.help_text = help_text
        self.start_time = start_time
        self.end_time = end_time

    def get_bound_field(self, form, field_name):
        return HoursExceptionBoundField(form, self, field_name)


class PayrollExceptionForm(ModelForm):
    captcha = ReCaptchaField()
    exception_date = DateField(widget=DatePicker(attrs={"min": now().isoformat(), "max": (now() + timedelta(weeks=4)).isoformat(), "date-format": "iso"}))
    exception_start_time = TimeField(widget=widgets.TimeInput)
    exception_end_time = TimeField(widget=widgets.TimeInput)

    class Meta:
        model = PayrollException
        fields = ("exception_date", "exception_start_time", "exception_end_time", "reason")

    def save(self):
        super().save()
        formatted_exception_date = get(self.exception_date).format("YYYY-mm-dd")
        formatted_exception_start_time = get(self.exception_start_time).format("HH:mm")
        formatted_exception_end_time = get(self.exception_end_time).format("HH:mm")

        PayrollException(
            date=formatted_exception_date,
            start_time=formatted_exception_start_time,
            end_time=formatted_exception_end_time,
            num_hours=calculateExceptionHours(formatted_exception_start_time, formatted_exception_end_time),
            reason=self.reason,
            requesting_employee=self.request.user.pk,
        )

    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"autocomplete": "off", "form_id": "employment-application"}
        self.fields["captcha"].label = False
        self.form_action = "create-exception"
        self.helper.layout = Layout(
            Row(Column("exception_date", css_class="form-group col-12"), css_class="form-row"),
            Row(Column("reason", css_class="form-group col-12"), css_class="form-row"),
            Row(
                Column("exception_start_time", css_id="exception-start-time", css_class="form-group col-4"),
                Column("exception_end_time", css_id="exception-end-time", css_class="form-group col-4"),
                css_class="form-row",
            ),
            Row(
                Column("captcha", css_class="form-group col-6"),
                HTML(
                    """
                <div class="form-group col-6 mb-0">
                 <label class="form-label">Number of Hours<em>Auto-Calculated</em></label>
                 <h5 class="textinput form-control" id="exception-hours" readonly>0</h5>
                 </div>
                 </div>
                    ),"""
                ),
                css_class="form-row",
            ),
            Row(Column(Submit(name="submit", value="Submit Exception", css_class="btn btn-success"))),
        )
