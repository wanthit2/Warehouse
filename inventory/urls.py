from django.urls import path
from .views import home, create_user,category_view, my_view, order_view, create_order, \
    delete_order , other_view  # เพิ่ม create_order
from . import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('create-user/', views.create_user, name='create_user'),
    path('categories/', views.category_view, name='category_view'),
    path('orders/', views.order_view, name='order_view'),
    path('my-url/', views.my_view, name='my_view'),
    path('create-order/', views.create_order, name='create_order'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('other-page/', views.other_view, name='other_view'),

    path('sales/', views.sales_view, name='sales_view'),
    path('status/', views.status_view, name='status_view'),
    path('update_status/<int:order_id>/', views.update_status, name='update_status'),
    path('products/add/', views.add_product, name='add_product'),  # ฟอร์มเพิ่มสินค้า
    path('products/', views.products, name='products'),
    path('product1/<int:product_id>/', views.product_view, name='product_view'),
    path('order/create/<int:product_id>/', views.order_create, name='order_create'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]

