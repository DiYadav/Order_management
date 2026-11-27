from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Inventory
from django.db import transaction
from decimal import Decimal


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


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(
        many=True,
        allow_empty=False
    )

    def validate_items(self, items):
        product_ids = [
            item["product_id"]
            for item in items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "A product cannot appear more than once in an order."
            )

        return items

    def create(self, validated_data):
        items_data = validated_data["items"]
        customer = self.context["request"].user

        product_ids = [
            item["product_id"]
            for item in items_data
        ]
        with transaction.atomic():

            inventories = Inventory.objects.select_for_update().select_related("product").filter(product_id__in=product_ids)
            inventory_map = {
                inventory.product_id: inventory
                for inventory in inventories
            }

            if len(inventory_map) != len(product_ids):
                raise serializers.ValidationError(
                    "One or more products do not have inventory."
                )

            total_amount = Decimal("0.00")
            order_items = []
            inventory_updates = []

            for item in items_data:
                product_id = item["product_id"]
                quantity = item["quantity"]
                inventory = inventory_map[product_id]
                product = inventory.product

                if not product.is_active:
                    raise serializers.ValidationError(
                        f"{product.name} is not available."
                    )

                if inventory.available_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {inventory.available_quantity}."
                    )

                unit_price = product.price
                subtotal = unit_price * quantity
                total_amount += subtotal
                order_items.append(
                    {
                        "product": product,
                        "quantity": quantity,
                        "unit_price": unit_price,
                    }
                )

                inventory.available_quantity -= quantity
                inventory_updates.append(inventory)

            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount
            )

            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"]
                )

            for inventory in inventory_updates:
                inventory.save(
                    update_fields=[
                        "available_quantity",
                        "updated_at"
                    ]
                )
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    status=serializers.ChoiceField(choices=Order.OrderStatus.choices)