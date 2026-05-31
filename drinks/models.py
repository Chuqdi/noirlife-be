from django.db import models
from users.models import User
from django.utils import timezone


    


class Drink(models.Model):
    drink_name = models.CharField(max_length=100)
    abvLvl = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    date_created = models.DateTimeField(
        default=timezone.now
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    