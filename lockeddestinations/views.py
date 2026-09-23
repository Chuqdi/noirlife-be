from utils.ResponseGenerator import ResponseGenerator
from .models import LockedDestination
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from .serializers import LockedDestinationSerializer




class LockedDestinationView(APIView):
    def get(self, request):
        lockedDestination = LockedDestination.objects.filter(
            user=request.user,
            is_completed=False,
            is_cancelled=False,
        ).order_by("-id")[:1]
        return ResponseGenerator.response(
            data=LockedDestinationSerializer(lockedDestination, many=True).data,
            status=status.HTTP_200_OK,
            message="Returned"
        )

    def post(self, request):
        data = {
            **request.data,
            "user":request.user.id,
        }
        serializer = LockedDestinationSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Saved"
            )
        

        return ResponseGenerator.response(
            data={},
            status=status.HTTP_400_BAD_REQUEST,
            message="Saving error"
        )
        
        
        
        
class LockedDestinationDetailView(APIView):
    """
    GET  /lockeddestinations/<id>/  — fetch a single locked destination
    put /lockeddestinations/<id>/ — edit starting point / destination / etc.
    """

    def get(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
        except LockedDestination.DoesNotExist:
            return ResponseGenerator.response(
                data={},
                message="Not found",
                status=status.HTTP_404_NOT_FOUND
            )

        return ResponseGenerator.response(
            data=LockedDestinationSerializer(l).data,
            status=status.HTTP_200_OK,
            message="Returned"
        )

    def put(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
        except LockedDestination.DoesNotExist:
            return ResponseGenerator.response(
                data={},
                message="Not found",
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LockedDestinationSerializer(
            l, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Updated"
            )

        return ResponseGenerator.response(
            data={},
            status=status.HTTP_400_BAD_REQUEST,
            message="Update error"
        )


class MarkLockedDestionView(APIView):
    """Existing 'mark as completed' action — unchanged behavior, ownership check added."""

    def post(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
            l.is_completed = True
            l.save()
        except LockedDestination.DoesNotExist:
            pass

        return ResponseGenerator.response(
            data={},
            message="Updated",
            status=status.HTTP_202_ACCEPTED
        )


class MarkArrivedView(APIView):
    def post(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
            l.arrived_at = timezone.now()
            l.save()
        except LockedDestination.DoesNotExist:
            pass

        return ResponseGenerator.response(
            data={},
            message="Updated",
            status=status.HTTP_202_ACCEPTED
        )


class MarkLeftView(APIView):
    def post(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
            l.left_at = timezone.now()
            l.save()
        except LockedDestination.DoesNotExist:
            pass

        return ResponseGenerator.response(
            data={},
            message="Updated",
            status=status.HTTP_202_ACCEPTED
        )


class MarkDriftedView(APIView):
    def post(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
            l.drifted_at = timezone.now()
            l.save()
        except LockedDestination.DoesNotExist:
            pass

        return ResponseGenerator.response(
            data={},
            message="Updated",
            status=status.HTTP_202_ACCEPTED
        )


class CancelLockedDestinationView(APIView):
    def post(self, request, id):
        try:
            l = LockedDestination.objects.get(id=id, user=request.user)
            l.is_cancelled = True
            l.save()
        except LockedDestination.DoesNotExist:
            pass

        return ResponseGenerator.response(
            data={},
            message="Cancelled",
            status=status.HTTP_202_ACCEPTED
        )
        