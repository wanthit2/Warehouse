from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Order, Product, Store, Stock

# การแสดงผลของ Order ใน Admin
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

# ลงทะเบียน Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ['product_name', 'product_code', 'description', 'price', 'quantity', 'image']  # ไม่ใส่ 'store'
    list_display = ['product_name', 'product_code', 'price', 'quantity', 'total_value']
    list_filter = ['product_name', 'price', 'quantity']
    search_fields = ['product_name', 'product_code']

# ลงทะเบียน Stock Admin
class StockAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity', 'price', 'added_date')
    list_filter = ('added_date',)
    search_fields = ('product_name',)

admin.site.register(Stock, StockAdmin)
