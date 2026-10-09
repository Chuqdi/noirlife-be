import hmac
import json
import logging
from datetime import datetime, timedelta, timezone as dt_timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PremiumAccess, ProcessedWebhookEvent

logger = logging.getLogger(__name__)
User = get_user_model()

NIGHT_PASS_PRODUCT_ID = "noir_night_pass"
NIGHT_PASS_HOURS = 24  # change here if you want 48h

SUBSCRIPTION_EVENTS = {
    "INITIAL_PURCHASE",
    "RENEWAL",
    "UNCANCELLATION",
    "PRODUCT_CHANGE",
    "CANCELLATION",
    "EXPIRATION",
    "BILLING_ISSUE",
}


def _ms_to_dt(ms):
    if ms is None:
        return None
    return datetime.fromtimestamp(int(ms) / 1000, tz=dt_timezone.utc)


class RevenueCatWebhookView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        expected = f"Bearer {settings.REVENUECAT_WEBHOOK_AUTH}"
        provided = request.headers.get("Authorization", "")
        if not hmac.compare_digest(provided.encode(), expected.encode()):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = request.data if isinstance(request.data, dict) else json.loads(request.body)
        except (ValueError, TypeError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event = payload.get("event") or {}
        event_id = event.get("id")
        event_type = event.get("type", "")
        app_user_id = event.get("app_user_id") or ""

        if not event_id or app_user_id.startswith("$RCAnonymousID"):
            return Response({"ok": True})  # nothing to attach to a user

        try:
            user = User.objects.get(pk=app_user_id)
        except (User.DoesNotExist, ValueError):
            logger.warning("RevenueCat event for unknown user %s", app_user_id)
            return Response({"ok": True})

        try:
            with transaction.atomic():
                ProcessedWebhookEvent.objects.create(event_id=event_id, event_type=event_type)
                access, _ = PremiumAccess.objects.select_for_update().get_or_create(user=user)
                self._apply(access, event_type, event)
                access.save()
        except IntegrityError:
            pass  # duplicate delivery, already processed

        return Response({"ok": True})

    def _apply(self, access: PremiumAccess, event_type: str, event: dict) -> None:
        product_id = event.get("product_id", "")

        if event_type in SUBSCRIPTION_EVENTS:
            expires = _ms_to_dt(event.get("expiration_at_ms"))
            if expires is not None:
                access.subscription_expires_at = expires
            access.product_id = product_id
            access.period_type = event.get("period_type", "") or access.period_type

        elif event_type == "NON_RENEWING_PURCHASE" and product_id == NIGHT_PASS_PRODUCT_ID:
            purchased = _ms_to_dt(event.get("purchased_at_ms"))
            # Reject stale values so an old replayed purchase can't grant access
            base = max(purchased, access.night_pass_until or purchased) if purchased else None
            if base is not None:
                access.night_pass_until = base + timedelta(hours=NIGHT_PASS_HOURS)


class BillingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        access = PremiumAccess.objects.filter(user=request.user).first()
        return Response(
            {
                "is_premium": bool(access and access.is_premium),
                "has_subscription": bool(access and access.has_subscription),
                "subscription_expires_at": access.subscription_expires_at if access else None,
                "night_pass_until": access.night_pass_until if access and access.has_night_pass else None,
            }
        )