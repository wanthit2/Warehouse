from django.urls import path
from .views import home, create_user, list_users, category_view, my_view, order_view, create_order, \
    delete_order , other_view  # เพิ่ม create_order
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('create-user/', views.create_user, name='create_user'),
    path('users/', views.list_users, name='list_users'),
    path('categories/', views.category_view, name='category_view'),
    path('orders/', views.order_view, name='order_view'),
    path('my-url/', views.my_view, name='my_view'),
    path('products/', views.products, name='products'),
    path('create-order/', views.create_order, name='create_order'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('other-page/', views.other_view, name='other_view'),
    path('homepage/', views.homepage, name='homepage'),
    path('sales/', views.sales_view, name='sales_view'),
    path('status/', views.status_view, name='status_view'),
    path('filter/', views.filter_view, name='filter_view'),
    path('update_status/<int:order_id>/', views.update_status, name='update_status'),
    path('register/', views.register, name='register'),  # ตั้ง URL สำหรับฟังก์ชัน register
]
