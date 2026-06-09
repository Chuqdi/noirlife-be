from .views import MemoryAPIView
from django.urls import path



urlpatterns = [
    path("", MemoryAPIView.as_view())
]
