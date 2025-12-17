from django.db import models
import uuid
from .managers import OrderManager

class OrderStatus(models.TextChoices):
    PENDING = 'pending'
    PAID = 'paid'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    FAILED = 'failed'

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    status = models.CharField(
        max_length=255, 
        choices=OrderStatus.choices, 
        default=OrderStatus.PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    items = models.JSONField(default=list)
    user_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = OrderManager()
    class Meta:
        db_table = 'orders'


