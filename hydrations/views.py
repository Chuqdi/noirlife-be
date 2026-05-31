from utils.ResponseGenerator import ResponseGenerator
from rest_framework import status
from rest_framework.views import APIView
from .serializers import HydrationSerializer
from .models import Hydration
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncHour, TruncDate, TruncWeek




class CreateHydrationView(APIView):
    def post(self, request):
        data = {**request.data, "user":request.user.pk}
        serializer = HydrationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
                message="Hydration created"
            )
        return ResponseGenerator.response(
            data={},
            status=status.HTTP_400_BAD_REQUEST,
            message="Error creating hydration"
        )
        
        



class TodayHydrationView(APIView):
    def get(self, request):
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        total_glasses = Hydration.objects.filter(
            user=request.user,
            date_logged__gte=today_start
        ).aggregate(total=Sum("number_of_glasses"))["total"] or 0

        return ResponseGenerator.response(
            data={"total_glasses": total_glasses},
            status=status.HTTP_200_OK,
            message="Success"
        )


class HydrationChartView(APIView):
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

        hydrations = Hydration.objects.filter(
            user=request.user,
            date_logged__gte=start_date
        )

        if period == "today":
            grouped = (
                hydrations
                .annotate(bucket=TruncHour("date_logged"))
                .values("bucket")
                .annotate(total=Sum("number_of_glasses"))
                .order_by("bucket")
            )
            labels = [f"{entry['bucket'].astimezone().strftime('%H')}h" for entry in grouped]
            data = [entry["total"] for entry in grouped]

        elif period == "week":
            grouped = (
                hydrations
                .annotate(bucket=TruncDate("date_logged"))
                .values("bucket")
                .annotate(total=Sum("number_of_glasses"))
                .order_by("bucket")
            )
            labels = [entry["bucket"].strftime("%a") for entry in grouped]
            data = [entry["total"] for entry in grouped]

        elif period == "month":
            grouped = (
                hydrations
                .annotate(bucket=TruncWeek("date_logged"))
                .values("bucket")
                .annotate(total=Sum("number_of_glasses"))
                .order_by("bucket")
            )
            labels = [f"W{i+1}" for i, _ in enumerate(grouped)]
            data = [entry["total"] for entry in grouped]

        elif period == "3months":
            grouped = (
                hydrations
                .annotate(bucket=TruncDate("date_logged"))
                .values("bucket")
                .annotate(total=Sum("number_of_glasses"))
                .order_by("bucket")
            )
            month_map: dict = {}
            for entry in grouped:
                month = entry["bucket"].strftime("%b")
                month_map[month] = month_map.get(month, 0) + entry["total"]
            labels = list(month_map.keys())
            data = list(month_map.values())

        else:
            labels = ["No data"]
            data = [0]

        if not labels:
            labels = ["No data"]
            data = [0]

        return ResponseGenerator.response(
            data={"labels": labels, "data": data},
            status=status.HTTP_200_OK,
            message="Success"
        )


class FilterHydrationView(APIView):
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
        hydrations = Hydration.objects.filter(
            user=request.user,
            date_logged__gte=start_date
        ).order_by("-date_logged")

        if limit:
            try:
                hydrations = hydrations[:int(limit)]
            except ValueError:
                pass

        serializer = HydrationSerializer(hydrations, many=True)
        return ResponseGenerator.response(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message="Success"
        )