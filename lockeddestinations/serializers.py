from .models import LockedDestination
from rest_framework import serializers


class LockedDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = LockedDestination
        read_only_fields = (
            "is_completed",
            "is_cancelled",
            "arrived_at",
            "left_at",
            "drifted_at",
            "date_time_started",
        )