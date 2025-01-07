# admin.py

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Order, Product


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product_name', 'price', 'quantity', 'total_price', 'status', 'image')
    list_filter = ('status',)  # กรองตามสถานะ

    def total_price(self, obj):
        return obj.total_price  # เรียกใช้ @property เพื่อคำนวณราคารวม
    total_price.admin_order_field = 'price'  # การสั่งเรียงตามราคารวม

# ลงทะเบียนแอดมิน
admin.site.register(Order, OrderAdmin)



# ปรับแต่งการแสดงผลของ User ใน Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')  # เพิ่มฟิลด์ที่ต้องการ
    search_fields = ('username', 'email')  # ค้นหาผู้ใช้ตามชื่อผู้ใช้และอีเมล
    ordering = ('username',)  # จัดเรียงตามชื่อผู้ใช้


# ยกเลิกการลงทะเบียน User แบบเดิมแล้วลงทะเบียน User ใหม่
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'quantity')  # ฟิลด์ที่แสดงในหน้า Admin
    search_fields = ('product_code', 'product_name')  # เพิ่มช่องค้นหา
