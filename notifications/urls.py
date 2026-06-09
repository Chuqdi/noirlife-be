from .views import MarkNotificationAsRead, NotificationAPIView, GetUserUnreadNotificationsCount
from django.urls import path




urlpatterns = [
    path("", NotificationAPIView.as_view()),
    path("unread_notifications_count/", GetUserUnreadNotificationsCount.as_view()),
    path("<int:id>/", MarkNotificationAsRead.as_view()),
    
]
