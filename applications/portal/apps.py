from django.apps import AppConfig


class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.portal"

    def ready(self):
        import common.signals  # no-qa
