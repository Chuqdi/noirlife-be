from django.conf import settings
from django.db import models
from django.utils import timezone


class PremiumAccess(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="premium_access"
    )
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    night_pass_until = models.DateTimeField(null=True, blank=True)
    product_id = models.CharField(max_length=100, blank=True)
    period_type = models.CharField(max_length=20, blank=True)  # TRIAL, INTRO, NORMAL
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_subscription(self) -> bool:
        return bool(self.subscription_expires_at and self.subscription_expires_at > timezone.now())

    @property
    def has_night_pass(self) -> bool:
        return bool(self.night_pass_until and self.night_pass_until > timezone.now())

    @property
    def is_premium(self) -> bool:
        return self.has_subscription or self.has_night_pass

    def __str__(self) -> str:
        return f"PremiumAccess<{self.user_id}>"


class ProcessedWebhookEvent(models.Model):
    """Makes the webhook idempotent, since RevenueCat may redeliver events."""

    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)