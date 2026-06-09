from .views import ToggleFavouriteView, FavouriteView, ReviewView
from django.urls import path


urlpatterns = [
    path("", FavouriteView.as_view()),
    path("toggle_favourite/<place_id>/", ToggleFavouriteView.as_view()),
    path("review/<place_id>/", ReviewView.as_view()),
]
