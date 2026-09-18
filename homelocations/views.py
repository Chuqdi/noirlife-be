from django.shortcuts import render
from utils.ResponseGenerator import ResponseGenerator
from rest_framework import status
from rest_framework.views import APIView
from .models import HomeLocation
from .serializers import HomeLocationSerializer


class HomeLocationView(APIView):
    def get(self, request):
        try:
            home = HomeLocation.objects.get(user=request.user)
            return ResponseGenerator.response(
                data=HomeLocationSerializer(home).data,
                status=status.HTTP_200_OK,
                message="Returned"
            )
        except HomeLocation.DoesNotExist:
            return ResponseGenerator.response(
                data={},
                status=status.HTTP_404_NOT_FOUND,
                message="No home set"
            )

    def post(self, request):
        home, _ = HomeLocation.objects.update_or_create(
            user=request.user,
            defaults={
                "coords": request.data.get("coords"),
                "address_name": request.data.get("address_name"),
            },
        )
        return ResponseGenerator.response(
            data=HomeLocationSerializer(home).data,
            status=status.HTTP_200_OK,
            message="Saved"
        )

    def delete(self, request):
        HomeLocation.objects.filter(user=request.user).delete()
        return ResponseGenerator.response(
            data={},
            status=status.HTTP_204_NO_CONTENT,
            message="Removed"
        )