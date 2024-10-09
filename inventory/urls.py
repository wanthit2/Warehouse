from django.urls import path
from .views import home, create_user, list_users, category_view, your_view, my_view, order_view

urlpatterns = [
    path('', home, name='home'),
    path('create-user/', create_user, name='create_user'),
    path('users/', list_users, name='list_users'),
    path('categories/', category_view, name='category_view'),
    path('orders/', order_view, name='order_view'),  # URL สำหรับแสดงคำสั่งซื้อ
    path('your-url/', your_view, name='your_view'),  # URL สำหรับ your_view
    path('my-url/', my_view, name='my_view'),
]