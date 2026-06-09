from django.db import models
from users.models import User
from django.utils import timezone


class Notification(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
