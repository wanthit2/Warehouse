from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test

# ฟังก์ชันเช็คว่าเป็นแอดมินหรือไม่
def admin_required(function):
    return user_passes_test(lambda u: u.is_staff)(function)

urlpatterns = [
    path('homepage/', views.home, name='homepage'),
    path('', views.home, name='home'),
    path('home1/', views.home1, name='home1'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('create-user/', views.create_user, name='create_user'),
    path('categories/', views.category_view, name='category_view'),
    path('orders/', views.order_view, name='order_view'),
    path('my-url/', views.my_view, name='my_view'),
    path('create-order/', views.create_order, name='create_order'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('sales/', views.sales_view, name='sales_view'),
    path('status/', views.status_view, name='status_view'),
    path('update_status/<int:order_id>/', views.update_status, name='update_status'),
    path('products/add/', views.add_product, name='add_product'),  # ฟอร์มเพิ่มสินค้า
    path('products/', views.products, name='products'),
    path('product1/<int:product_id>/', views.product_view, name='product_view'),
    path('profile/', views.profile, name='profile'),
    path('graph/', views.graph_view, name='graph_view'),
    path('order_list/', views.order_list, name='order_list'),
    path('order/create/<int:product_id>/', views.order_create, name='order_create'),
    path('order/confirmation/<int:product_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/success/', views.order_success, name='order_success'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/success/', lambda request: print("ย้ายไปที่หน้า order_success แล้ว")),
    path('profile/', views.profile, name='profile'),
    path('create_profile/', views.create_profile, name='create_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('admin/orders/add/', views.add_order, name='add_order'),
    path('admin/orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),

    #adminstock
    path('admin/stores/', views.store_list, name='store_list'),  # แสดงร้านค้าทั้งหมด
    path('admin/stores/<int:store_id>/stock/', views.store_stock, name='store_stock'),  # แสดงสต็อกของร้าน
    path('admin/stores/<int:store_id>/stock/add/', views.add_stock, name='add_stock'),  # เพิ่มสินค้าในสต็อก
    path('admin/stores/stock/edit/<int:stock_id>/', views.edit_stock, name='edit_stock'),  # แก้ไขสต็อก
    path('admin/stores/stock/delete/<int:stock_id>/', views.delete_stock, name='delete_stock'),  # ลบสินค้าในสต็อก
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
    #URL ของร้าน
    path('stores/', views.store_list, name='store_list'),
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),

    #stock
    path('stock_view/', views.stock_view, name='stock_view'),
    path('create_stock/', views.create_stock, name='create_stock'),
    path('update_stock/', views.update_stock, name='update_stock'),
    path('create-product/', views.create_product, name='create_product'),

    #หน้ารายการ
    path('product/<int:id>/', views.product_detail_view, name='product_detail_view'),
    path('product/edit/<int:id>/', views.edit_product, name='edit_product'),
]
