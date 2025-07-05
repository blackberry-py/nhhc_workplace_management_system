from django.apps import AppConfig
from loguru import logger


class AnnouncementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.announcements"

    def ready(self):
        super().ready()
        logger.info(f"{self.name} ready() method called")
