from django.urls import path

from .views import BillingStatusView, RevenueCatWebhookView

urlpatterns = [
    path("webhooks/revenuecat/", RevenueCatWebhookView.as_view(), name="revenuecat-webhook"),
    path("status/", BillingStatusView.as_view(), name="billing-status"),
]