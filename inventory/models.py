from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.apps import apps
from django.db.models.signals import pre_save, post_save, post_delete





### 🔹 โมเดลผู้ใช้ (Custom User)
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'แอดมิน'),
        ('shop_owner', 'เจ้าของร้าน'),
        ('customer', 'ลูกค้า'),
    ]

    username = models.CharField(max_length=150, unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer',
        verbose_name="ประเภทผู้ใช้"
    )

    is_superadmin = models.BooleanField(default=False, verbose_name='ซุปเปอร์แอดมิน')
    is_shop_owner = models.BooleanField(default=False, verbose_name='เจ้าของร้าน')
    is_admin = models.BooleanField(default=False, verbose_name='แอดมิน')
    is_shop_owner_requested = models.BooleanField(default=False)
    is_shop_owner_approved = models.BooleanField(default=False)
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


class Shop(models.Model):
    name = models.CharField(max_length=255, verbose_name="ชื่อร้าน")
    location = models.CharField(max_length=255, blank=True, default="ที่อยู่ยังไม่ได้กำหนด", verbose_name="ที่ตั้งร้าน")
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="owned_shops", verbose_name="เจ้าของร้าน"
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="admin_shops", blank=True, verbose_name="แอดมินร้านค้า"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้างร้าน")

    class Meta:
        verbose_name = "ร้านค้า"
        verbose_name_plural = "ร้านค้าทั้งหมด"

    def __str__(self):
        return self.name


### 🔹 โมเดลประเภทสินค้า (Category)
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="หมวดหมู่")

    def __str__(self):
        return self.name

### 🔹 โมเดลสินค้า (Product)
class Product(models.Model):
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, verbose_name="ร้านค้า")
    product_name = models.CharField(max_length=255, default='Default Product Name', verbose_name='ชื่อสินค้า')
    product_code = models.CharField(max_length=100, unique=True, verbose_name='รหัสสินค้า')
    description = models.TextField(blank=True, null=True, verbose_name='รายละเอียดสินค้า')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    image = models.ImageField(upload_to='img/', blank=True, null=True, verbose_name="รูปสินค้า")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="จำนวนสินค้าคงคลัง")
    added_date = models.DateTimeField(default=timezone.now, verbose_name="วันที่เพิ่มสินค้า")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    UNIT_CHOICES = [
        ('kg', 'กิโลกรัม'),
        ('pcs', 'ชิ้น'),
    ]
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs', verbose_name="หน่วยสินค้า")

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="สถานะสินค้า")

    class Meta:
        verbose_name = 'สินค้า'
        verbose_name_plural = 'สินค้าทั้งหมด'

    def __str__(self):
        return f"{self.product_name} ({self.product_code}) - {self.get_unit_display()}"

    @property
    def total_value(self):
        return self.price * self.stock_quantity

    def save(self, *args, **kwargs):
        """ อัปเดต stock_quantity ตาม quantity เมื่อเพิ่มสินค้าใหม่ """
        if not self.pk:  # เฉพาะตอนเพิ่มสินค้าใหม่
            self.stock_quantity = self.quantity
        super().save(*args, **kwargs)




### 🔹 สร้างรหัสสินค้าอัตโนมัติ
@receiver(pre_save, sender=Product)
def generate_product_code(sender, instance, **kwargs):
    """ ✅ สร้างรหัสสินค้าอัตโนมัติถ้ายังไม่มี """
    if not instance.product_code:
        last_product = Product.objects.all().order_by('id').last()
        if last_product and last_product.product_code.startswith("P"):
            try:
                last_id = int(last_product.product_code[1:])  # ✅ แปลงรหัสสินค้าให้เป็นตัวเลข
                new_code = f"P{last_id + 1:03d}"  # ✅ เพิ่มตัวเลขอัตโนมัติ เช่น P001 → P002
            except ValueError:
                new_code = "P001"  # ✅ กรณีที่มีข้อผิดพลาด
        else:
            new_code = "P001"
        instance.product_code = new_code


### 🔹 โมเดลคลังสินค้า (Stock)
class Stock(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name="ร้านค้า", null=True, blank=True)
    product = models.ForeignKey(Product, related_name="stock", on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    added_date = models.DateField(auto_now_add=True, verbose_name="วันที่เพิ่มสินค้า")
    description = models.TextField(verbose_name="รายละเอียดสินค้า", blank=True, null=True)

    class Meta:
        verbose_name = "สินค้าในคลัง"
        verbose_name_plural = "สินค้าในคลังทั้งหมด"

    def __str__(self):
        product_name = self.product.product_name if self.product else "ไม่มีสินค้า"
        shop_name = self.shop.name if self.shop else "ไม่มีร้านค้า"
        return f"{product_name} - {shop_name}"





### 🔹 โมเดลคำสั่งซื้อ (Order)
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)  # ✅ ใช้ order_id เป็น primary key แทน id
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    status = models.CharField(max_length=50, verbose_name='สถานะ', default='Pending')
    image = models.ImageField(upload_to='product_images/', verbose_name='รูปสินค้า', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='ผู้ใช้งาน')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='ร้านค้า', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Order {self.order_id}: {self.product.product_name if self.product else 'ไม่มีสินค้า'} - {self.quantity} ชิ้น"




### 🔹 โมเดลโปรไฟล์ผู้ใช้ (UserProfile)
class UserProfile(models.Model):
    user = models.OneToOneField("inventory.CustomUser", on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)  # ✅ ฟิลด์ที่อยู่ของผู้ใช้
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"


### 🔹 โมเดลคำขอเป็นเจ้าของร้าน (ShopOwnerRequest)
class ShopOwnerRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    description = models.TextField()
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name


### 🔹 โมเดลซัพพลายเออร์ (Supplier)
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField()

    def __str__(self):
        return self.name



