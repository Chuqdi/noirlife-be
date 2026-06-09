from rest_framework.serializers import ModelSerializer
from .models import FavouritedPlace, Review



class ReviewSerializer(ModelSerializer):
    class Meta:
        fields ="__all__"
        model = Review

class FavouritedPlaceSerializer(ModelSerializer):
    class Meta:
        fields ="__all__"
        model = FavouritedPlace