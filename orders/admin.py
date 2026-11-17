from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "total_amount",
        "status",
        "order_date",
    )
    list_filter = ("status", "order_date")
    search_fields = (
        "customer__email",
        "id",
    )
    ordering = ("-order_date",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "unit_price",
    )
    search_fields = (
        "product__name",
        "order__id",
    )
