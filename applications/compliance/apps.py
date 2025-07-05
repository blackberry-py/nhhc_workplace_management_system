from django.apps import AppConfig
from loguru import logger


class ComplianceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.compliance"

    def ready(self):
        super().ready()
        logger.info(f"{self.name} ready() method called")
