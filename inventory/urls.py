from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test

from .views import AddShopView


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


    path('request_shop_owner/', views.request_shop_owner, name='request_shop_owner'),
    path('success/', views.success_page, name='success_page'),

    #adminstock
    path('admin_home/', views.admin_home_view, name='admin_home'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject_user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('request_status/<int:user_id>/', views.request_status, name='request_status'),
    path('manage_shops/', views.manage_shops, name='manage_shops'),
    path('shop_detail/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    #path('approve-shop-request/<int:request_id>/', views.approve_shop_request, name='approve_shop_request'),
    #path('reject-shop-request/<int:request_id>/', views.reject_shop_request, name='reject_shop_request'),
    path('request_status/<int:user_id>/', views.request_status, name='request_status'),

    #URL ของร้าน
    path('stores/', views.store_list, name='store_list'),
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
    path('add_admin/', views.add_admin, name='add_admin'),
    path('shop/<int:shop_id>/products/', views.product_list, name='product_list'),
    path('shop/<int:shop_id>/add_product/', views.add_product, name='add_product'),
    path('add-shop/', AddShopView.as_view(), name='add_shop'),
    path('edit-shop/<int:shop_id>/', views.edit_shop, name='edit_shop'),
    path('delete-shop/<int:shop_id>/', views.delete_shop, name='delete_shop'),
    path('shop-list/', views.shop_list, name='shop_list'),
    path('create/', views.create_shop, name='create_shop'),
    path('admin-shop/', views.admin_home_shop, name='admin_homeshop'),
    path('admin_delete_order/<int:order_id>/', views.admin_delete_order, name='admin_delete_order'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),




    #stock
    path('create_stock/', views.create_stock, name='create_stock'),
    path('update_stock/', views.update_stock, name='update_stock'),
    path('create-product/', views.create_product, name='create_product'),

    #หน้ารายการ
    path('product/<int:id>/', views.product_detail_view, name='product_detail_view'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),

    path('shop-owner-request/', views.shop_owner_request, name='shop-owner-request'),  # สำหรับหน้าขอเป็นเจ้าของร้าน
    path('shop-owner-request-success/', views.shop_owner_request_success, name='shop-owner-request-success'),

    path('stock/', views.stock_view, name='stock_view'),
    path('add-stock/', views.stock_add, name='stock_add'),  # เพิ่มสต็อก
    path('edit/<int:id>/', views.stock_edit, name='stock_edit'),
    path('delete/<int:id>/', views.stock_delete, name='stock_delete'),

    #จัดการadmin
    path('manage_admins/<int:shop_id>/', views.manage_shop_admins, name='manage_admins'),
    path('shop/<int:shop_id>/manage_admins/', views.manage_shop_admins, name='manage_shop_admins'),
    path('manage-products/<int:shop_id>/', views.manage_products, name='manage_products'),
    path('admin_order_list/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/', views.order_list, name='order_list'),  # คำสั่งซื้อทั้งหมด
    path('admin/orders/completed/', views.order_list, {'status': 'completed'}, name='completed_orders'),
    # คำสั่งซื้อที่ดำเนินการแล้ว
    path('admin/orders/pending/', views.order_list, {'status': 'pending'}, name='pending_orders'),
    # คำสั่งซื้อที่รอดำเนินการ

]
