from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
)


class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user).select_related("customer" ).prefetch_related("items__product")
        serializer = OrderSerializer(orders,many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        response_serializer = OrderSerializer(order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        order = get_object_or_404(Order.objects.filter(customer=request.user)
            .select_related("customer")
            .prefetch_related("items__product"),pk=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
