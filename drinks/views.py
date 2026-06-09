from utils.ResponseGenerator import ResponseGenerator
from .serializers import DrinkSerializer
from .models import Drink
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncHour, TruncDate, TruncWeek






class SingleDrinkAPIView(APIView):
    def delete(self, request, id):
        try:
            drink = Drink.objects.get(id = id)
            drink.delete()
        except Drink.DoesNotExist as e:
            pass
        return ResponseGenerator.response(
            data={},
            status=status.HTTP_200_OK,
            message="Deleted"
        )

class DrinkView(APIView):
    def post(self, request):
        data = {**request.data, "user": request.user.id}
        serializer = DrinkSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
                message="Created"
            )
        return ResponseGenerator.response(
            data={},
            status=status.HTTP_400_BAD_REQUEST,
            message="Error creating drink"
        )





class DrinkChartView(APIView):
    def get(self, request):
        period = request.query_params.get("period", "today")
        now = timezone.now()

        period_map = {
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "week": now - timedelta(days=7),
            "month": now - timedelta(days=30),
            "3months": now - timedelta(days=90),
        }

        start_date = period_map.get(period, period_map["today"])

        drinks = Drink.objects.filter(
            user=request.user,
            date_created__gte=start_date
        )

        # ── Group by appropriate time bucket ────────────────────────────────
        if period == "today":
            # Group by hour → labels: "0h", "6h", "12h", "18h"
            grouped = (
                drinks
                .annotate(bucket=TruncHour("date_created"))
                .values("bucket")
                .annotate(total=Count("id"))
                .order_by("bucket")
            )
            labels = [f"{entry['bucket'].astimezone().strftime('%H')}h" for entry in grouped]
            data = [entry["total"] for entry in grouped]

        elif period == "week":
            # Group by day → labels: "Mon", "Tue" ...
            grouped = (
                drinks
                .annotate(bucket=TruncDate("date_created"))
                .values("bucket")
                .annotate(total=Count("id"))
                .order_by("bucket")
            )
            labels = [entry["bucket"].strftime("%a") for entry in grouped]
            data = [entry["total"] for entry in grouped]

        elif period == "month":
            # Group by week → labels: "W1", "W2" ...
            grouped = (
                drinks
                .annotate(bucket=TruncWeek("date_created"))
                .values("bucket")
                .annotate(total=Count("id"))
                .order_by("bucket")
            )
            labels = [f"W{i+1}" for i, _ in enumerate(grouped)]
            data = [entry["total"] for entry in grouped]

        elif period == "3months":
            # Group by month → labels: "Jan", "Feb" ...
            grouped = (
                drinks
                .annotate(bucket=TruncDate("date_created"))
                .values("bucket")
                .annotate(total=Count("id"))
                .order_by("bucket")
            )
            # Re-group by month name
            month_map: dict = {}
            for entry in grouped:
                month = entry["bucket"].strftime("%b")
                month_map[month] = month_map.get(month, 0) + entry["total"]
            labels = list(month_map.keys())
            data = list(month_map.values())

        else:
            labels = ["No data"]
            data = [0]

        # Fallback if no drinks in range
        if not labels:
            labels = ["No data"]
            data = [0]

        return ResponseGenerator.response(
            data={"labels": labels, "data": data},
            status=status.HTTP_200_OK,
            message="Success"
        )
        
class FilterDrinksView(APIView):
    def get(self, request):
        period = request.query_params.get("period", "today")
        limit = request.query_params.get("limit", None)
        now = timezone.now()

        period_map = {
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "week": now - timedelta(days=7),
            "month": now - timedelta(days=30),
            "3months": now - timedelta(days=90),
        }

        start_date = period_map.get(period, period_map["today"])
        drinks = Drink.objects.filter(
            user=request.user,
            date_created__gte=start_date
        ).order_by("-date_created")

        if limit:
            try:
                drinks = drinks[:int(limit)]
            except ValueError:
                pass

        serializer = DrinkSerializer(drinks, many=True)
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message="Success"
        )