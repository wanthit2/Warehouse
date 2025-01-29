from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Order, Product, Store, Stock
# การแสดงผลของ Order ใน Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product_name', 'price', 'quantity', 'status', 'user', 'store', 'total_price')  # เพิ่มฟิลด์ store
    list_filter = ('status', 'store')  # กรองตามสถานะและร้าน
    search_fields = ('product_name', 'order_id', 'user__username')  # ค้นหาตามชื่อสินค้า, รหัสคำสั่งซื้อ, และผู้ใช้

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset  # ถ้าเป็น superuser ให้เห็นทุกร้าน
        return queryset.filter(store__owner=request.user.username)  # กรองร้านตามเจ้าของร้านที่ล็อกอินอยู่

    def total_price(self, obj):
        return obj.total_price  # เรียกใช้ @property เพื่อคำนวณราคารวม
    total_price.admin_order_field = 'total_price'  # การสั่งเรียงตาม total_price

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
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'description')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)  # กรองร้านของผู้ใช้งานที่ล็อกอิน

class StockAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity', 'price', 'store')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(store__owner=request.user)  # กรองตามเจ้าของร้าน

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_code', 'price', 'quantity', 'store')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(store__owner=request.user)  # กรองตามเจ้าของร้าน

admin.site.register(Store, StoreAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Product, ProductAdmin)

