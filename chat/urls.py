from django.urls import path
from .views import (
    customer_chat_view, admin_chat_view, admin_chat_list_view,
    chat_history_api, chat_messages_api, customer_chat_list_view
)

urlpatterns = [
    path("customer-chat/<int:product_id>/", customer_chat_view, name="customer_chat"),
    path("admin-chat/<int:session_id>/", admin_chat_view, name="admin_chat"),
    path("admin-chat-list/", admin_chat_list_view, name="admin_chat_list"),
    path("api/chat/messages/<int:session_id>/", chat_messages_api, name="chat_messages_api"),
    path("api/chat/history/<int:session_id>/", chat_history_api, name="chat_history_api"),
    path("customer-chat-list/", customer_chat_list_view, name="customer_chat_list"),
    path("customer-chat/<int:session_id>/", customer_chat_view, name="customer_chat_detail"),


]