from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Inventory
from .serializers import InventorySerializer


class InventoryListCreateAPIView(APIView):
    def get(self, request):
        inventory = Inventory.objects.select_related("product").all()
        serializer = InventorySerializer(inventory,many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class InventoryDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Inventory,pk=pk)

    def get(self, request, pk):
        inventory = self.get_object(pk)
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)

    def patch(self, request, pk):
        inventory = self.get_object(pk)
        serializer = InventorySerializer(inventory,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
