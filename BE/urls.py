# views.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

def test(request):
    return render(request,  "emails/welcome.html", {"name":"Hezekiah"})





@csrf_exempt
@require_POST
def twilio_status_webhook(request):
    message_sid = request.POST.get("MessageSid")
    message_status = request.POST.get("MessageStatus")  # queued, sent, delivered, undelivered, failed
    error_code = request.POST.get("ErrorCode")
    print(request.POST)

    # Update your own records here, e.g. find the message by SID and save the status
    print(message_sid, message_status, error_code)

    return HttpResponse(status=204)


urlpatterns = [
    path("api/messaging/webhooks/status/", twilio_status_webhook),
    
    
    path("test/", test),
    path("admin/", admin.site.urls),
    path("users/",include("users.urls")),
    path("drinks/",include("drinks.urls")),
    path("trustedcontacts/",include("trustedcontacts.urls")),
    path("hydrations/",include("hydrations.urls")),
    path("chat/",include("chats.urls")),
    path("memories/",include("memories.urls")),
    path("notifications/",include("notifications.urls")),
    path("places/",include("places.urls")),
    path("lockeddestinations/",include("lockeddestinations.urls")),
    path("homelocations/",include("homelocations.urls")),
    path("locations/",include("locations.urls")),
    path("billings/",include("billings.urls")),
]
