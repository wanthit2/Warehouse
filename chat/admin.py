from django.contrib import admin
from .models import ChatSession, Message

# Register ChatSession ให้แสดงใน Django Admin
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'admin', 'created_at', 'is_resolved')
    search_fields = ('customer__username', 'admin__username')
    list_filter = ('is_resolved', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'text', 'timestamp')
    search_fields = ('sender__username', 'text')
    list_filter = ('timestamp',)
