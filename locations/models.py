from django.conf import settings
from django.db import models

class UserLocationPing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="location_pings")
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     ordering = ["-updated_at"]