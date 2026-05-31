from .views import ChatSessionDetailView, ChatSessionListCreateView, SendMessageView
from django.urls import path

urlpatterns = [
    path("sessions/", ChatSessionListCreateView.as_view()),
    path("sessions/<int:session_id>/", ChatSessionDetailView.as_view()),
    path("sessions/<int:session_id>/messages/", SendMessageView.as_view()),
]
