from django.db import models

from users.models import User

# Create your models here.



class HomeLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="home_location")
    address_name = models.CharField(max_length=700, null=True, blank=True)
    coords = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)