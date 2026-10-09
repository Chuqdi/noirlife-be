from rest_framework.permissions import BasePermission

from .models import PremiumAccess


class IsPremium(BasePermission):
    message = "Noir+ required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        access = PremiumAccess.objects.filter(user=user).first()
        return bool(access and access.is_premium)