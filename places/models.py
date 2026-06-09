from django.db import models
from users.models import User
from django.utils import timezone



class FavouritedPlace(models.Model):
    place_id = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_favourited = models.DateTimeField(default=timezone.now)
    
class Review(models.Model):
    place_id = models.CharField(max_length=500)
    stars = models.CharField(max_length=300)
    review = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_reviewed = models.DateTimeField(default=timezone.now)
    
    