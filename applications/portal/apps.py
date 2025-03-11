from django.apps import AppConfig


class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.portal"

    def ready(self):
        super().ready()
        import common.signals  # no-qa
