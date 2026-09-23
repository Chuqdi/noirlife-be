from django.db import models
from django.utils import timezone

from users.models import User


class LockedDestination(models.Model):
    class Status(models.TextChoices):
        NOW = "now"
        SCHEDULED = "scheduled"

    schedule_type = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NOW,
    )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    starting_point_name = models.CharField(max_length=700)
    destination_address_name = models.CharField(max_length=700, null=True, blank=True)
    destination_name = models.CharField(max_length=700)
    starting_coords = models.JSONField()
    ending_coords = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    arrived_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    drifted_at = models.DateTimeField(null=True, blank=True)
    expected_return_time = models.DateTimeField(null=True, blank=True)
    date_time_started = models.DateTimeField(default=timezone.now)

    # Celery task id for the pending "scheduled trip starting" notification,
    # so it can be revoked if the user cancels before the scheduled time.
    notification_task_id = models.CharField(max_length=255, null=True, blank=True)

    # Celery task ids for the 4 return-check-in tasks (prepare / check_15 /
    # check_30 / check_45), keyed by name, so they can be bulk-revoked on
    # cancellation or rescheduled if expected_return_time changes.
    checkin_task_ids = models.JSONField(null=True, blank=True, default=dict)