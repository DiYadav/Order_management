from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product
from decimal import Decimal


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING="PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    customer=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    order_date=models.DateTimeField(auto_now_add=True)
    total_amount=models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status=models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    def __str__(self):
        return f" Order {self.id} - {self.customer.email}"

    class Meta:
        ordering=["-order_date"]

class OrderItem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product=models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} * {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    class Meta:
        constraints=[
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="order_item_quantity_gte_1"
            )
        ]
    