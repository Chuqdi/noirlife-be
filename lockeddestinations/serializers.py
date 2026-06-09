from .models import LockedDestination
from rest_framework import serializers

class LockedDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        fields ="__all__"
        model = LockedDestination