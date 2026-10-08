import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

User = get_user_model()

ACTIVE_EVENTS = {
    "INITIAL_PURCHASE",   # may be a trial start (period_type == "TRIAL")
    "RENEWAL",            # includes trial -> paid conversion
    "PRODUCT_CHANGE",
    "UNCANCELLATION",
    "NON_RENEWING_PURCHASE",
}

# EXPIRATION fires when a trial ends without converting, or a sub lapses.
# CANCELLATION = auto-renew turned off; access continues until EXPIRATION.
# BILLING_ISSUE = payment failed; access continues during grace period,
# and EXPIRATION fires if it is never resolved.
INACTIVE_EVENTS = {"EXPIRATION"}


@csrf_exempt
@require_POST
def revenuecat_webhook(request):
    expected = f"Bearer {settings.REVENUECAT_WEBHOOK_SECRET}"
    if request.headers.get("Authorization") != expected:
        return HttpResponseForbidden()

    payload = json.loads(request.body)
    event = payload.get("event", {})
    event_type = event.get("type")
    app_user_id = event.get("app_user_id")
    period_type = event.get("period_type")  # "TRIAL", "INTRO", or "NORMAL"

    try:
        user = User.objects.get(pk=app_user_id)
    except (User.DoesNotExist, ValueError):
        return HttpResponse(status=200)  # ack so RevenueCat doesn't retry forever

    if event_type in ACTIVE_EVENTS:
        user.is_pro = True
        user.is_trial = period_type == "TRIAL"
    elif event_type in INACTIVE_EVENTS:
        user.is_pro = False
        user.is_trial = False
    else:
        return HttpResponse(status=200)

    user.save(update_fields=["is_pro", "is_trial"])
    return HttpResponse(status=200)