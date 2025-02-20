# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Stock  # import โมเดลที่เกี่ยวข้อง




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Order)
def update_stock(sender, instance, created, **kwargs):
    if created:  # ถ้าเป็นการเพิ่มคำสั่งซื้อใหม่
        for item in instance.items.split(','):  # สมมติรายการใน order เป็น list ของสินค้า (เช่น 'product1,product2')
            product_name, quantity_ordered = item.split(":")
            quantity_ordered = int(quantity_ordered)

            # หา stock ที่ตรงกับชื่อสินค้าจาก store
            try:
                stock = Stock.objects.get(product_name=product_name, store=instance.store)
                if stock.quantity >= quantity_ordered:
                    stock.quantity -= quantity_ordered  # ลดจำนวนสินค้าในสต๊อก
                    stock.save()
                else:
                    raise ValueError(f"จำนวนสินค้าในสต๊อกไม่เพียงพอสำหรับสินค้า: {product_name}")
            except Stock.DoesNotExist:
                raise ValueError(f"ไม่พบสินค้าในสต๊อก: {product_name}")

