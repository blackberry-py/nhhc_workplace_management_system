from django.apps import AppConfig
from loguru import logger

class EmployeeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.employee"
    label = "nhhc_employee"
    verbose_name = "Agency Employee"

    def ready(self):
        super().ready()
        logger.info(f"{self.name} ready() method called")