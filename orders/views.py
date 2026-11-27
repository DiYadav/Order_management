from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer, 
    OrderStatusUpdateSerializer,
)
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from inventory.models import Inventory



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



class OrderStatusUpdateAPIView(APIView):

    permission_classes = [IsAdminUser]

    allowed_transitions = {
        Order.OrderStatus.PENDING: [
            Order.OrderStatus.CONFIRMED
        ],
        Order.OrderStatus.CONFIRMED: [
            Order.OrderStatus.SHIPPED
        ],
        Order.OrderStatus.SHIPPED: [
            Order.OrderStatus.DELIVERED
        ],
    }

    def patch(self, request, pk):

        with transaction.atomic():

            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=pk
            )

            serializer = OrderStatusUpdateSerializer(
                data=request.data
            )

            serializer.is_valid(raise_exception=True)

            new_status = serializer.validated_data["status"]

            if new_status == Order.OrderStatus.CANCELLED:
                raise ValidationError(
                    "Use the cancel endpoint to cancel an order."
                )

            allowed_statuses = self.allowed_transitions.get(
                order.status,
                []
            )

            if new_status not in allowed_statuses:
                raise ValidationError(
                    f"Cannot change order status from "
                    f"{order.status} to {new_status}."
                )

            order.status = new_status

            order.save(
                update_fields=["status"]
            )

        return Response(
            OrderSerializer(order).data
        )


class OrderCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update().filter(
                    customer=request.user
                ),
                pk=pk
            )

            if order.status not in [
                Order.OrderStatus.PENDING,
                Order.OrderStatus.CONFIRMED,
            ]:
                raise ValidationError(
                    "Only pending or confirmed orders can be cancelled."
                )

            order_items = list(
                order.items.all()
            )

            product_ids = sorted({
                item.product_id
                for item in order_items
            })

            inventories = Inventory.objects.select_for_update().filter(
                product_id__in=product_ids
            ).order_by("product_id")

            inventory_map = {
                inventory.product_id: inventory
                for inventory in inventories
            }

            if len(inventory_map) != len(product_ids):
                raise ValidationError(
                    "Inventory record is missing for one or more products."
                )

            for item in order_items:
                inventory = inventory_map[item.product_id]
                inventory.available_quantity += item.quantity

                inventory.save(
                    update_fields=[
                        "available_quantity",
                        "updated_at",
                    ]
                )
            order.status = Order.OrderStatus.CANCELLED
            order.save(update_fields=["status"])

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )
