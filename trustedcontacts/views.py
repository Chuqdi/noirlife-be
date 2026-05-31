from utils.ResponseGenerator import ResponseGenerator
from rest_framework import status
from .serializers import TrustedContactSerializer
from rest_framework.views import APIView
from .models import TrustedContact



class TrustContactView(APIView):
    def post(self, request):
        data = {**request.data, "user": request.user.id}
        serializer = TrustedContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                message="Saved",
                status=status.HTTP_201_CREATED
            )
        return ResponseGenerator.response(
            data={},
            message="Error saving",
            status=status.HTTP_400_BAD_REQUEST
        )


class TrustContactDetailView(APIView):
    def get_object(self, pk, user):
        try:
            return TrustedContact.objects.get(pk=pk, user=user)
        except TrustedContact.DoesNotExist:
            return None

    def post(self, request, pk):  # ✅ matches your component's post call
        contact = self.get_object(pk, request.user)
        if not contact:
            return ResponseGenerator.response(
                data={},
                message="Contact not found",
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TrustedContactSerializer(
            contact,
            data={**request.data, "user": request.user.id},
            partial=True  # ✅ allows partial updates
        )
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                message="Updated",
                status=status.HTTP_200_OK
            )
        return ResponseGenerator.response(
            data={},
            message="Error updating",
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        contact = self.get_object(pk, request.user)
        if not contact:
            return ResponseGenerator.response(
                data={},
                message="Contact not found",
                status=status.HTTP_404_NOT_FOUND
            )
        contact.delete()
        return ResponseGenerator.response(
            data={},
            message="Deleted",
            status=status.HTTP_204_NO_CONTENT
        )
        
        
class TrustContactView(APIView):
    def post(self, request):
        data = {**request.data, "user":request.user.id}
        serializer = TrustedContactSerializer(
            data =data
        )
        
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                message="Saved",
                status=status.HTTP_201_CREATED
            )
        return ResponseGenerator.response(
            data={},
            message="Error saving",
            status=status.HTTP_400_BAD_REQUEST
        )
