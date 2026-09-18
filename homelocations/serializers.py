from .models import HomeLocation
from rest_framework import serializers



class HomeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeLocation
        fields = "__all__"
        read_only_fields = ("user", "updated_at")