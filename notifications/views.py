from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import status
from utils.ResponseGenerator import ResponseGenerator
from rest_framework.views import APIView


class MarkNotificationAsRead(APIView):
    def put(self, request, id):
        try:
            notification = Notification.objects.get(id =id)
            notification.is_read=True
            notification.save()
            return ResponseGenerator.response(
                data = {},
                status=status.HTTP_200_OK,
                message="Notifications"
            )
        except Notification.DoesNotExist as e:
            return ResponseGenerator.response(
                data={},
                message="Error returning notification",
                status=status.HTTP_400_BAD_REQUEST
            )



class GetUserUnreadNotificationsCount(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(
            user = request.user,
            is_read=False
        )
        
        return ResponseGenerator.response(
            data=notifications.count(),
            message="Notifications",
            status=status.HTTP_200_OK
        )
        

class NotificationAPIView(APIView):
    def post(self, request):
        data = {**request.data, "user":request.user.id}
        serializer = NotificationSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                message="Notifications",
                status=status.HTTP_200_OK
            )
        return ResponseGenerator.response(
                data={},
                message="Error retrieving notifications",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
    def get (self, request):
        notifications = Notification.objects.filter(user = request.user)
        
        return ResponseGenerator.response(
            data=NotificationSerializer(notifications, many=True).data,
            message="Notifications",
            status=status.HTTP_200_OK
                                          
            )
    
