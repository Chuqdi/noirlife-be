from .views import TrustContactDetailView, TrustContactView
from django.urls import path


urlpatterns = [
    path("", TrustContactView.as_view()),
    path("<int:pk>/", TrustContactDetailView.as_view()),
]
