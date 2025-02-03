# inventory/models.py
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings



class Member(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member_profile')

    def __str__(self):
        return self.user.username

from django.conf import settings

class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name='ชื่อร้าน')
    description = models.TextField(verbose_name='รายละเอียดร้าน', null=True, default="ไม่มีข้อมูล")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="เจ้าของร้าน")
    location = models.CharField(max_length=255, verbose_name="ที่ตั้งร้าน", null=True, blank=True)
    class Meta:
        verbose_name = 'ร้านค้า'
        verbose_name_plural = 'ร้านค้าทั้งหมด'

    def __str__(self):
        return self.name



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

    is_superadmin = models.BooleanField(default=False, verbose_name='ซุปเปอร์แอดมิน')  # ✅ เพิ่มฟิลด์นี้
    is_shop_owner = models.BooleanField(default=False, verbose_name='เจ้าของร้าน')
    is_admin = models.BooleanField(default=False, verbose_name='แอดมิน')
    is_shop_owner_requested = models.BooleanField(default=False)
    is_shop_owner_approved = models.BooleanField(default=False)
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    stores = models.ManyToManyField(Store, related_name='owners', blank=True)  # ความสัมพันธ์ Many-to-Many กับ Store

    def __str__(self):
        return self.username



# โมเดล Store





from django.contrib.auth import get_user_model



class Shop(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=False, default="ที่อยู่ยังไม่ได้กำหนด")  # กำหนด default
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_shops', blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# โมเดล Product
class Product(models.Model):
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, default=1)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', verbose_name='ร้าน', null=True, blank=True)
    product_name = models.CharField(max_length=255, default='Default Product Name', verbose_name='ชื่อสินค้า')
    product_code = models.CharField(max_length=100, unique=True, verbose_name='รหัสสินค้า')
    description = models.TextField(blank=True, null=True, verbose_name='รายละเอียดสินค้า')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    image = models.ImageField(upload_to='img/', blank=True, null=True, verbose_name="รูปสินค้า")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="จำนวนสินค้าคงคลัง")
    added_date = models.DateTimeField(default=timezone.now, verbose_name="วันที่เพิ่มสินค้า")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    # ✅ เพิ่มฟิลด์ `status`
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
        return f"{self.product_name} ({self.product_code})"

    @property
    def total_value(self):
        return self.price * self.stock_quantity

    # ฟังก์ชันสำหรับคืนค่าร้านที่เชื่อมโยง
    def get_store_name(self):
        return self.store.name if self.store else self.shop.name
  # ใช้ store ถ้ามี มิฉะนั้นใช้ shop

class Stock(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='ร้านค้า', null=True)
    product_name = models.CharField(max_length=100, verbose_name='ชื่อสินค้า')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    added_date = models.DateField(auto_now_add=True, verbose_name='วันที่เพิ่มสินค้า')
    description = models.TextField(verbose_name='รายละเอียดสินค้า', blank=True, null=True)

    class Meta:
        verbose_name = 'สินค้าในคลัง'
        verbose_name_plural = 'สินค้าในคลังทั้งหมด'

    def __str__(self):
        return self.product_name


# สร้างรหัสสินค้าอัตโนมัติ
@receiver(pre_save, sender=Product)
def generate_product_code(sender, instance, **kwargs):
    if not instance.product_code:  # ถ้ารหัสสินค้าไม่มีค่า
        last_product = Product.objects.all().order_by('id').last()  # หาสินค้าล่าสุด
        if last_product:
            last_id = int(last_product.product_code[1:])  # ตัด "P" ออกแล้วแปลงเป็นเลข
            new_code = f"P{last_id + 1:03d}"  # เพิ่มลำดับ
        else:
            new_code = "P001"  # กรณีแรกเริ่ม
        instance.product_code = new_code


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255, verbose_name='ชื่อสินค้า', null=True, blank=True)
    product_code = models.CharField(max_length=255, verbose_name='รหัสสินค้า', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    status = models.CharField(max_length=50, verbose_name='สถานะ', default='Pending')
    image = models.ImageField(upload_to='product_images/', verbose_name='รูปสินค้า', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='ผู้ใช้งาน')
    store = models.ForeignKey('Store', on_delete=models.CASCADE, verbose_name='ร้านค้า', null=True, blank=True)
    items = models.ManyToManyField('Product', related_name='orders', blank=True)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, verbose_name='ร้านค้า', null=True, blank=True)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product_name




@login_required  # บังคับให้ผู้ใช้ต้องล็อกอินก่อนสร้างคำสั่งซื้อ
def order_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # รับจำนวนสินค้า (quantity) จากแบบฟอร์ม
        quantity = int(request.POST.get('quantity', 1))

        # คำนวณราคาทั้งหมด
        total_price = product.price * quantity

        # สร้างคำสั่งซื้อ
        order = Order.objects.create(
            product=product,
            customer=request.user,  # ใช้ข้อมูลผู้ใช้ปัจจุบัน
            quantity=quantity,
            total_price=total_price,
        )

        # นำผู้ใช้ไปยังหน้ายืนยันคำสั่งซื้อ
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'order_create.html', {'product': product})



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"



class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user_type = models.CharField(
        max_length=50,
        choices=[('shop', 'ร้านค้า'), ('admin', 'ผู้ดูแลระบบ')],
        default='shop'
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'รออนุมัติ'), ('approved', 'อนุมัติแล้ว')],
        default='pending'  # กำหนดสถานะเริ่มต้นเป็น 'pending'
    )

    def __str__(self):
        return self.user.username



class ShopOwnerRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ใช้ AUTH_USER_MODEL
    store_name = models.CharField(max_length=255)
    description = models.TextField()
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.store_name

