from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Order, Stock, Product


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



### 🔹 ลด Stock เมื่อมีการสั่งซื้อ
@receiver(post_save, sender=Order)
def reduce_stock_on_order(sender, instance, created, **kwargs):
    if created:  # ✅ ทำงานเมื่อคำสั่งซื้อถูกสร้างใหม่
        if not instance.product:
            print(f"⚠️ คำสั่งซื้อ ID {instance.order_id} ไม่มีสินค้า ไม่สามารถลด Stock ได้!")
            return

        try:
            # ✅ ลดจำนวนสินค้าในคลัง Stock
            stock = Stock.objects.filter(product=instance.product, shop=instance.shop).first()
            if stock:
                if stock.quantity >= instance.quantity:
                    stock.quantity -= instance.quantity  # ✅ ลดจำนวนสินค้าใน Stock
                    stock.save()
                    print(f"✅ อัปเดตสต๊อกสำเร็จ! คงเหลือ: {stock.quantity} ชิ้น")
                else:
                    print(f"⚠️ สินค้า {instance.product.product_name} ไม่พอในสต๊อก!")
            else:
                print(f"⚠️ ไม่พบ Stock สำหรับสินค้า {instance.product.product_name}")

        except Stock.DoesNotExist:
            print(f"⚠️ ไม่พบสินค้า {instance.product.product_name} ในสต๊อก!")




### 🔹 ลบ Stock เมื่อสินค้าถูกลบ
@receiver(post_delete, sender=Product)
def delete_product_stock(sender, instance, **kwargs):
    try:
        print(f"🗑️ กำลังลบสินค้า {instance.product_name} จาก Stock...")
        Stock.objects.filter(product=instance).delete()
        print(f"✅ สินค้า {instance.product_name} ถูกลบจาก Stock แล้ว")
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดในการลบ Stock: {e}")



@receiver(post_save, sender=Product)
def update_stock_on_create(sender, instance, created, **kwargs):
    if created:  # ทำงานเมื่อเพิ่มสินค้าใหม่
        instance.stock_quantity = instance.quantity
        instance.save()
