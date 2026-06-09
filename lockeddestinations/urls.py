from .views import LockedDestinationView, MarkLockedDestionView
from django.urls import path


urlpatterns = [
    path("", LockedDestinationView.as_view()),
    path("mark_as_completed/<id>/", MarkLockedDestionView.as_view())
]
