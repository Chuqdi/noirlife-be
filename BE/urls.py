

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def test(request):
    return render(request,  "emails/welcome.html", {"name":"Hezekiah"})
urlpatterns = [
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
]
