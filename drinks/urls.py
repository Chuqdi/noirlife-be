from .views import DrinkChartView, DrinkView, FilterDrinksView
from django.urls import path


urlpatterns = [
    path("", DrinkView.as_view()),
    path("filter/", FilterDrinksView.as_view()),
    path("chart/", DrinkChartView.as_view()),
]
