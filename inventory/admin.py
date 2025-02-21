from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Order, Product, Shop, Stock, CustomUser  # เปลี่ยน Store เป็น Shop

# ใช้ get_user_model() ถ้าคุณใช้ CustomUser
User = get_user_model()

# 📌 การแสดงผลของ Order ใน Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product', 'price', 'quantity', 'status', 'user', 'shop', 'total_price')
    list_filter = ('status', 'shop')  # เปลี่ยน store เป็น shop
    search_fields = ('product', 'order_id', 'user__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(shop__owner=request.user)  # เปลี่ยน store__owner เป็น shop__owner

    def total_price(self, obj):
        return obj.total_price
    total_price.admin_order_field = 'total_price'

admin.site.register(Order, OrderAdmin)

# 📌 ลงทะเบียน CustomUser ใน Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

# 📌 ลงทะเบียน Shop ใน Admin
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'created_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)  # แสดงเฉพาะร้านของผู้ใช้ที่ล็อกอิน

admin.site.register(Shop, ShopAdmin)

# 📌 ปรับ StockAdmin ให้ใช้ Shop แทน Store
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price', 'shop')  # เปลี่ยน store เป็น shop

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(shop__owner=request.user)  # เปลี่ยน store__owner เป็น shop__owner

admin.site.register(Stock, StockAdmin)

# 📌 ปรับ ProductAdmin ให้ใช้ Shop แทน Store
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_code', 'price', 'quantity', 'shop')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(shop__owner=request.user)  # เปลี่ยน store__owner เป็น shop__owner

admin.site.register(Product, ProductAdmin)


from .models import Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)