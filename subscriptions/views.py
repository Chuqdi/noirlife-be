# subscriptions/views.py
import hmac
from datetime import datetime, timezone as dt_tz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Subscription, WebhookEvent

User = get_user_model()

ACTIVE_TYPES = {"INITIAL_PURCHASE", "RENEWAL", "UNCANCELLATION", "PRODUCT_CHANGE",
                "NON_RENEWING_PURCHASE"}

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def revenuecat_webhook(request):
    auth = request.headers.get("Authorization", "")
    print(auth)
    print(settings.REVENUECAT_WEBHOOK_AUTH)
    # if not hmac.compare_digest(auth, settings.REVENUECAT_WEBHOOK_AUTH):
    #     return Response(status=401)

    event = request.data.get("event", {})
    event_id, etype = event.get("id"), event.get("type")
    app_user_id = event.get("app_user_id", "")

    try:
        user = User.objects.get(pk=app_user_id)
    except (User.DoesNotExist, ValueError):
        return Response({"ok": True})  # anonymous/unknown id: ack so RC doesn't retry forever

    try:
        with transaction.atomic():
            WebhookEvent.objects.create(event_id=event_id, type=etype, payload=request.data)
            sub, _ = Subscription.objects.select_for_update().get_or_create(user=user)

            exp_ms = event.get("expiration_at_ms")
            if exp_ms:
                sub.expires_at = datetime.fromtimestamp(exp_ms / 1000, tz=dt_tz.utc)
            sub.product_id = event.get("product_id", sub.product_id)

            if etype in ACTIVE_TYPES:
                sub.is_active = True
                sub.is_trial = event.get("period_type") == "TRIAL"
                sub.will_renew = True
                sub.billing_issue = False
            elif etype == "CANCELLATION":
                sub.will_renew = False   # still active until expires_at
            elif etype == "BILLING_ISSUE":
                sub.billing_issue = True
            elif etype == "EXPIRATION":
                sub.is_active = False
                sub.is_trial = False
                sub.will_renew = False
            sub.save()
    except IntegrityError:
        pass  # duplicate event, already processed

    return Response({"ok": True})