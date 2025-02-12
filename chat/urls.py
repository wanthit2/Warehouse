from django.urls import path
from .views import (
    chat_sessions, customer_chat_view, admin_chat_view, admin_chat_list_view,
    chat_messages_api, customer_chat_list_view
)

urlpatterns = [
    # ✅ API สำหรับดึง session
    path('api/chat-sessions/', chat_sessions, name="chat_sessions"),

    # ✅ หน้าสำหรับลูกค้า
    path("customer-chat/", customer_chat_view, name="customer_chat"),
    path("customer-chat/<int:product_id>/", customer_chat_view, name="customer_chat_with_product"),
    path("customer-chat/<int:session_id>/", customer_chat_view, name="customer_chat_detail"),
    path("customer-chat-list/", customer_chat_list_view, name="customer_chat_list"),

    # ✅ หน้าสำหรับแอดมินร้าน / SuperAdmin
    path("admin-chat/<int:session_id>/", admin_chat_view, name="admin_chat"),
    path("admin-chat-list/", admin_chat_list_view, name="admin_chat_list"),

    # ✅ API ดึงข้อความในแชท (ต้องใช้ `<int:session_id>/`)
    path("api/chat/messages/<int:session_id>/", chat_messages_api, name="chat_messages_api"),
]


