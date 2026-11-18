from rest_framework import serializers
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(
    source="product.name",
    read_only=True
    )
    class Meta:
        model=Inventory
        fields=["id","product","product_name","available_quantity","updated_at",]
        read_only_fields = ["id","updated_at",]

        