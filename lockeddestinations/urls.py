from django.urls import path
from .views import (
    LockedDestinationView,
    LockedDestinationDetailView,
    MarkLockedDestionView,
    MarkArrivedView,
    MarkLeftView,
    MarkDriftedView,
    CancelLockedDestinationView,
)

urlpatterns = [
    path("", LockedDestinationView.as_view()),
    path("<int:id>/", LockedDestinationDetailView.as_view()),
    path("mark_as_completed/<int:id>/", MarkLockedDestionView.as_view()),
    path("mark_arrived/<int:id>/", MarkArrivedView.as_view()),
    path("mark_left/<int:id>/", MarkLeftView.as_view()),
    path("mark_drifted/<int:id>/", MarkDriftedView.as_view()),
    path("cancel/<int:id>/", CancelLockedDestinationView.as_view()),
]