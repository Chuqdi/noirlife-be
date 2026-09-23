import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BE.settings")

app = Celery("BE")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
   
}


# app.conf.beat_schedule = {
#     "evaluate-trust-monthly": {
#         "task": "trust.tasks.evaluate_all_drivers",
#         "schedule": crontab(day_of_month="1", hour=0, minute=0),  # runs on the 1st of every month at midnight
#     },
# }