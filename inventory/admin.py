from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Order, Product, Store, Stock, Shop
from .models import CustomUser
# ใช้ get_user_model() ถ้าคุณใช้ CustomUser
User = get_user_model()

# การแสดงผลของ Order ใน Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product_name', 'price', 'quantity', 'status', 'user', 'store', 'total_price')
    list_filter = ('status', 'store')
    search_fields = ('product_name', 'order_id', 'user__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(store__owner=request.user)

    def total_price(self, obj):
        return obj.total_price
    total_price.admin_order_field = 'total_price'

admin.site.register(Order, OrderAdmin)

# ลงทะเบียน CustomUser ใน Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

# ลงทะเบียน Store, Product, Stock ใน Admin
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'description')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)

class StockAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity', 'price', 'store')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(store__owner=request.user)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_code', 'price', 'quantity', 'store')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(store__owner=request.user)


class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'created_at')  # ใช้ 'owner' แทน 'user'


admin.site.register(Store, StoreAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Shop)

