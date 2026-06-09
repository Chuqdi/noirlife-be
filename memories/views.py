from django.shortcuts import render
from utils.ResponseGenerator import ResponseGenerator
from rest_framework import status
from .models import Memory
from .serializers import MemorySerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser


class MemoryAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        data = { "user":request.user.pk, "image":request.FILES["image"]}
        serializer = MemorySerializer(data =data)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                message="Saved",
                status=status.HTTP_200_OK
            )
        print(serializer.errors)
        return ResponseGenerator.response(
            data={},
            message="Error saving memory",
            status=status.HTTP_400_BAD_REQUEST
        )
    def get(self, request):
        memories = Memory.objects.filter(user = request.user)
        return ResponseGenerator.response(
            data = MemorySerializer(memories, many=True).data,
            status=status.HTTP_200_OK,
            message="Memories retrieved"
        )
    