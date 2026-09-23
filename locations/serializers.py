# serializers.py
from rest_framework import serializers
from .models import UserLocationPing

class UserLocationPingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationPing
        fields = "__all__"