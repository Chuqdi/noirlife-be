# subscriptions/permissions.py
from rest_framework.permissions import BasePermission

class HasActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        sub = getattr(request.user, "subscription", None)
        return bool(sub and sub.has_access)