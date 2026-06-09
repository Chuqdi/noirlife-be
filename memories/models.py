from django.db import models
from django.utils import timezone
from users.models import User

class Memory (models.Model):
    image = models.ImageField()
    date_added = models.DateTimeField( default=timezone.now )
    user = models.ForeignKey(User, on_delete=models.CASCADE)