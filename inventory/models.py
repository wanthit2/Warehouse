# inventory/models.py
from django.db import models
from django.utils import timezone  # นำเข้า timezone
from django.contrib.auth.models import User
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True, verbose_name='รหัสคำสั่ง')
    order_date = models.DateField(default=timezone.now, verbose_name='วันที่')  # ตั้งค่าวันที่ปัจจุบันเป็นค่าเริ่มต้น
    customer = models.CharField(max_length=100, verbose_name='ลูกค้า')
    sales_channel = models.CharField(
        max_length=100,
        choices=[('store', 'หน้าร้าน'), ('online', 'ออนไลน์')],
        verbose_name='ช่องทางการขาย'
    )
    destination = models.CharField(max_length=100, verbose_name='ปลายทาง')
    items = models.PositiveIntegerField(default=1, verbose_name='จำนวนสินค้า')  # ตั้งค่าเริ่มต้น
    status = models.CharField(
        max_length=50,
        choices=[('pending','รอจัดส่ง'), ('shipped','จัดส่งแล้ว'), ('cancelled','ยกเลิก')],
        verbose_name='สถานะ'
    )

    class Meta:
        verbose_name = 'คำสั่งซื้อ'
        verbose_name_plural = 'คำสั่งซื้อทั้งหมด'

    def __str__(self):
        return self.customer
