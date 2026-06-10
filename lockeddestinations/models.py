from django.db import models
from django.utils import timezone
from users.models import User


class LockedDestination(models.Model):
    class Status(models.TextChoices):
        NOW   = "now"
        SCHEDULED = "scheduled"

    schedule_type = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NOW,
    )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    starting_point_name = models.CharField(max_length=700)
    destination_address_name= models.CharField(max_length=700, null=True, blank=True)
    destination_name = models.CharField(max_length=700)
    starting_coords = models.JSONField()
    ending_coords = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    date_time_started = models.DateTimeField(
        default=timezone.now
    )
    