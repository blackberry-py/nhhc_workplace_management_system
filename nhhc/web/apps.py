from django.apps import AppConfig
from health_check.plugins import plugin_dir


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web"

    def ready(self) -> None:
        super().ready()
        from nhhc.status import (
            UnitedHealthChecks,
            DocSealSigningServiceHealthCheck,
        )
        plugin_dir.register(UnitedHealthChecks)
        plugin_dir.register(DocSealSigningServiceHealthCheck)
 