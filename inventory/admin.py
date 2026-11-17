from django.contrib import admin
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "available_quantity",
        "updated_at",
    )
    search_fields = ("product__name",)
    ordering = ("-updated_at",)
