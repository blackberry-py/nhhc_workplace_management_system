import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging  # noqa
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nhhc.settings")

nhhc_workers = Celery("nhhc")
nhhc_workers.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig  # noqa

    from django.conf import settings  # noqa

    dictConfig(settings.LOGGING)


nhhc_workers.autodiscover_tasks()


@nhhc_workers.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
