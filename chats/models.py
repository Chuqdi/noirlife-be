from django.db import models
from django.utils import timezone
from users.models import User


class ChatSession(models.Model):
    """Represents a single conversation thread (new chat = new session)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=255, blank=True, null=True)  # auto-generated from first message
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_updated"]

    def __str__(self):
        return f"{self.user} - {self.title or 'Untitled'}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        MODEL = "model", "Model"

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=Role.choices)
    text = models.TextField(blank=True)
    file_uri = models.URLField(blank=True, null=True)       # stored file URL (S3, etc.)
    file_mime_type = models.CharField(max_length=100, blank=True, null=True)  # e.g. "image/jpeg"
    file_name = models.CharField(max_length=255, blank=True, null=True)
    is_image = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    # Self-referential FK — model reply points back to the user message that triggered it
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies"
    )

    class Meta:
        ordering = ["date_created"]

    def __str__(self):
        return f"[{self.role}] {self.text[:60]}"