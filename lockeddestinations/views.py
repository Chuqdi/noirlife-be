from utils.ResponseGenerator import ResponseGenerator
from .models import LockedDestination
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LockedDestinationSerializer




class MarkLockedDestionView(APIView):
    def post(self, request, id):
        try:
            l = LockedDestination.objects.get(
                id=id
            )
            l.is_completed=True
            l.save()
        except:
            pass
        
        return ResponseGenerator.response(
            data={},
            message="Updated",
            status=status.HTTP_202_ACCEPTED
        )
        
class LockedDestinationView(APIView):
    def get(self, request):
        lockedDestination = LockedDestination.objects.filter (
            user = request.user,
            is_completed =False
        ).order_by("-id")[:1]
        return ResponseGenerator.response(
            data=LockedDestinationSerializer(lockedDestination, many=True).data,
            status=status.HTTP_200_OK,
            message="Returned"
        )
    def post(self, request):
        data = {**request.data, "user":request.user.id}
        
        serializer = LockedDestinationSerializer(
            data=data
        )
        
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Saved"
            )
        
        print(serializer.errors)
        return ResponseGenerator.response(
            data={},
            status=status.HTTP_400_BAD_REQUEST,
            message="Saving error"
        )