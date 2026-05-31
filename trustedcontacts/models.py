from django.db import models
from django.utils import timezone
from users.models import User



class TrustedContact(models.Model):
    name =models.CharField(max_length=400)
    phone_number=models.CharField(max_length=400)
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return super().__str__()