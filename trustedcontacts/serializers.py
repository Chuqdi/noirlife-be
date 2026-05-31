from .models import TrustedContact
from rest_framework import serializers



class TrustedContactSerializer(serializers.ModelSerializer):
    class Meta:
        fields ="__all__"
        model =TrustedContact