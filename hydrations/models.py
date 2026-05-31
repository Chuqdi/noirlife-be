from django.db import models
from django.utils import timezone
from users.models import User

class Hydration(models.Model):
    number_of_glasses = models.IntegerField()
    date_logged = models.DateTimeField(
        default=timezone.now
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return super().__str__()