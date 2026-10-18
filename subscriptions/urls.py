from django.urls import path
from .views import revenuecat_webhook

urlpatterns = [
    path("revenue_cat/webhook",revenuecat_webhook)
]
