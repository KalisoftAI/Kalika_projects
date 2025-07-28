from django.db import models
from catalog.models import Product
import uuid

class PunchOutOrder(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40)
    buyer_cookie = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    return_url = models.CharField(max_length=500)
    buyer_identity = models.CharField(max_length=255)
    cxml_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PunchOut Order: {self.quantity} x {self.product.product_title} for {self.buyer_cookie}"

    class Meta:
        db_table = 'punchout_orders'