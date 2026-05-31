from .views import CreateHydrationView, FilterHydrationView, HydrationChartView, TodayHydrationView
from django.urls import path


urlpatterns = [
    path("",CreateHydrationView.as_view()),
    path("filter/", FilterHydrationView.as_view()),
    path("chart/", HydrationChartView.as_view()),
    path("today/", TodayHydrationView.as_view())
]
