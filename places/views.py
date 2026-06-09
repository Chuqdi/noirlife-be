from utils.ResponseGenerator import ResponseGenerator
from .models import FavouritedPlace, Review
from rest_framework.views import APIView
from rest_framework import status
from .serializers import FavouritedPlaceSerializer, ReviewSerializer



class ReviewView(APIView):
    def get(self, request, place_id):
        reviews = Review.objects.filter(
            place_id=place_id
        ).order_by("-id")[:10]
        return ResponseGenerator.response(
            data=ReviewSerializer(reviews, many=True).data,
             status=status.HTTP_200_OK,
             message="Saved"
        )
    def post(self, request, place_id):
        data = {**request.data, "user":request.user.id, "place_id":place_id}
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data, 
                message="Review",
                status=status.HTTP_201_CREATED
            )
        return ResponseGenerator.response(
                data={}, 
                message="Review",
                status=status.HTTP_400_BAD_REQUEST
            )
        
class FavouriteView(APIView):
    def get(self, request,):
        places = FavouritedPlace.objects.filter(
            user = request.user
        )
        return ResponseGenerator.response(
            data=FavouritedPlaceSerializer(places, many=True).data,
            message="Favourites",
            status=status.HTTP_200_OK
        )
        
        
class ToggleFavouriteView(APIView):
    def post(self, request, place_id):
        fv = FavouritedPlace.objects.filter(
            user = request.user,
            place_id=place_id
        )
        
        if fv.exists():
            fv.delete()
        else:
            FavouritedPlace.objects.create(
                place_id=place_id,
                user = request.user
            )
        
        return ResponseGenerator.response(
            data={},
            message="Favourite toggled",
            status=status.HTTP_200_OK
        )
