# admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Order
from .models import Product
from django.contrib import admin

# ปรับแต่งการแสดงผลของ Order ใน Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'customer', 'sales_channel', 'destination', 'items', 'status')
    search_fields = ('customer', 'sales_channel', 'destination')
    list_filter = ('status', 'sales_channel')

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