from django.shortcuts import render
from rest_framework.views import APIView
import threading
from homelocations.services import evaluate_home_location_update
from locations.services import evaluate_location_update
from lockeddestinations.models import LockedDestination
from .utils import updateUserLocation
from utils.ResponseGenerator import ResponseGenerator
from .serializers import UserLocationPingSerializer
from rest_framework import status



class UserLocationUpdatedAPIView(APIView):
    def post(self, request,):
        data = request.data
        user = request.user
        
        location = updateUserLocation(
            user, 
            data
        )
        serializer = UserLocationPingSerializer(location)
        
        
        lock = (
        LockedDestination.objects.filter(
            user=request.user,
            # is_completed=False,
            is_cancelled=False,
            )
            .order_by("-date_time_started")
            .first()
        )

        if lock is None:
            return ResponseGenerator.response(
                data={},
                message="",
                status=status.HTTP_200_OK
            )
            
        # t = threading.Thread(
        #     target=evaluate_location_update,
        #     kwargs={
        #         "user":request.user,
        #         "lock":lock,
        #         "latitude":data["latitude"],
        #         "longitude":data["longitude"],
        #         "accuracy":data.get("accuracy")
        #     }
        # )
        # t.start()
        
        
        # evaluate_location_update(
        #     user = request.user,
        #     lock=lock,
        #     latitude=data["latitude"],
        #     longitude =data["longitude"],
        #     accuracy = data.get("accuracy")
        # )
        
        evaluate_home_location_update(
            user = request.user,
            latitude=data["latitude"],
            longitude =data["longitude"],
            accuracy = data.get("accuracy")
        )
        
        
        
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message="Updated"
        )
