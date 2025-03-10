from allauth.account.forms import LoginForm
from formset.fields import Activator
from formset.renderers import ButtonVariant
from formset.widgets import Button


class NHHCLoginForm(LoginForm):
    submit = Activator(
        label="Submit",
        widget=Button(
            action="disable -> spinner -> delay(500) -> submit -> reload !~ scrollToError",
            button_variant=ButtonVariant.PRIMARY,
            icon_path="/send.svg",
        ),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)
