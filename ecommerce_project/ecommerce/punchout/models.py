from django.db import models

class PunchoutOrder(models.Model):
    session_key = models.CharField(max_length=40)
    cxml_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    supplier_id = models.CharField(max_length=255, blank=True)
    punchout_request_url = models.CharField(max_length=500, blank=True)
    punchout_response_url = models.CharField(max_length=500, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')

    def __str__(self):
        return f"Punchout Order {self.session_key} - {self.created_at}"

    class Meta:
        db_table = 'punchout_orders'