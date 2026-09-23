from .views import UserLocationUpdatedAPIView
from django.urls import path


urlpatterns = [
    path("update_user_location/", UserLocationUpdatedAPIView.as_view())
]
