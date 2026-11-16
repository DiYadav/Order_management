from django.db import models
from products.models import Product

class Inventory(models.Model):
    product=models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    available_quantity=models.PositiveIntegerField(default=0)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.available_quantity}"
    
