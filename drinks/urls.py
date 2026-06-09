from .views import DrinkChartView, DrinkView, FilterDrinksView, SingleDrinkAPIView
from django.urls import path


urlpatterns = [
    path("", DrinkView.as_view()),
    path("filter/", FilterDrinksView.as_view()),
    path("chart/", DrinkChartView.as_view()),
    path("<int:id>/", SingleDrinkAPIView.as_view()),
     
]
