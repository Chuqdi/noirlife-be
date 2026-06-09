from .models import Memory
from rest_framework import serializers


class MemorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Memory
        fields = ['id', 'image', 'image_url','user', 'date_added']
        extra_kwargs = {'image': {'write_only': True}}  # hide raw field, expose url instead

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url  # Cloudinary URL automatically
        return None