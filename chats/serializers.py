from rest_framework import serializers
from .models import Message, ChatSession


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id", "role", "text", "file_uri", "file_mime_type",
            "file_name", "is_image", "reply_to", "date_created"
        ]

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "title", "messages", "date_created", "date_updated"]