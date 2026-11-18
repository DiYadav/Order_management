from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    subtotal = serializers.ReadOnlyField()
    class Meta:
        model = OrderItem
        fields = ["id","product","product_name","quantity","unit_price","subtotal",]

        read_only_fields = ["id","subtotal",]


class OrderSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True
    )

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = ["id","customer","customer_email","order_date","total_amount","status","items",]
        read_only_fields = ["id","customer","order_date","total_amount","status",]
