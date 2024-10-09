# inventory/models.py

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):  # ย้ายออกจาก Product
    order_id = models.AutoField(primary_key=True)
    product = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    sales_channel = models.CharField(max_length=255)
    target = models.DecimalField(max_digits=10, decimal_places=2)
    score = models.IntegerField()
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.product
