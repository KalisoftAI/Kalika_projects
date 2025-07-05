from django.db import models

from django.db import models

class Product(models.Model):
    item_id = models.AutoField(primary_key=True)
    main_category = models.CharField(max_length=100)
    sub_categories = models.CharField(max_length=100, blank=True, null=True)
    item_code = models.CharField(max_length=50, unique=True)
    product_title = models.CharField(max_length=255)
    product_description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.product_title

    class Meta:
        db_table = 'products'  # Maps to the existing 'products' Table