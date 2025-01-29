# inventory/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # นำเข้า User จาก Django
from django.db.models.signals import pre_save
from django.dispatch import receiver
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')

    def __str__(self):
        return self.user.username


# โมเดล Store
class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name='ชื่อร้าน')
    description = models.TextField(verbose_name='รายละเอียดร้าน', null=True, default="ไม่มีข้อมูล")
    owner = models.CharField(max_length=100, default="Default Owner", verbose_name="เจ้าของร้าน")

    class Meta:
        verbose_name = 'ร้านค้า'
        verbose_name_plural = 'ร้านค้าทั้งหมด'

    def __str__(self):
        return self.name


# โมเดล Stock
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


# โมเดล Product
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', verbose_name='ร้าน', null=True, blank=True)
    product_name = models.CharField(max_length=255, default='Default Product Name', verbose_name='ชื่อสินค้า')
    product_code = models.CharField(max_length=100, unique=True, verbose_name='รหัสสินค้า')
    description = models.TextField(blank=True, null=True, verbose_name='รายละเอียดสินค้า')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    image = models.ImageField(upload_to='img/', blank=True, null=True, verbose_name="รูปสินค้า")

    class Meta:
        verbose_name = 'สินค้า'
        verbose_name_plural = 'สินค้าทั้งหมด'

    def __str__(self):
        return f"{self.product_name} ({self.product_code})"

    @property
    def total_value(self):
        return self.price * self.quantity


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
    order_id = models.AutoField(primary_key=True, verbose_name='ลำดับ')
    product_name = models.CharField(max_length=255, verbose_name='ชื่อสินค้า', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา')
    quantity = models.PositiveIntegerField(verbose_name='จำนวน')
    status = models.CharField(max_length=50, verbose_name='สถานะ', default='Pending')
    image = models.ImageField(upload_to='product_images/', verbose_name='รูปสินค้า', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='ผู้ใช้งาน')
    store = models.ForeignKey('Store', on_delete=models.CASCADE, verbose_name='ร้านค้า', null=True, blank=True)

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
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.username} Profile"


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username

