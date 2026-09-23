from django.db import models

from users.models import User


class HomeLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="home_location")
    address_name = models.CharField(max_length=700, null=True, blank=True)
    coords = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    # --- presence tracking ---
    # None = not yet determined (no ping evaluated yet)
    # True = currently considered home
    # False = currently considered away
    is_home = models.BooleanField(null=True, blank=True, default=True)
    left_home_at = models.DateTimeField(null=True, blank=True)
    arrived_home_at = models.DateTimeField(null=True, blank=True)