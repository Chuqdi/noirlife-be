# subscriptions/models.py
from django.conf import settings
from django.db import models

class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="subscription")
    product_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)
    is_trial = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    will_renew = models.BooleanField(default=True)
    billing_issue = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_access(self):
        from django.utils import timezone
        return self.is_active and (self.expires_at is None or self.expires_at > timezone.now())

class WebhookEvent(models.Model):  # idempotency + audit
    event_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)