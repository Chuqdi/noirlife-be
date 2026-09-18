from .views import HomeLocationView
from django.urls import path



urlpatterns = [
    path("", HomeLocationView.as_view()),
]
