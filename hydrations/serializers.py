from rest_framework import serializers
from .models import Hydration


class HydrationSerializer(serializers.ModelSerializer):
    class Meta:
        fields ="__all__"
        model = Hydration