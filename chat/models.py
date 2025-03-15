from django.db import models
from django.conf import settings
from inventory.models import Shop  # ✅ นำเข้า Shop

class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('open', 'เปิด'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('closed', 'ปิดแล้ว'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_sessions")
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_sessions", null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)  # ✅ เพิ่มฟิลด์ shop
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    # ✅ เพิ่มฟิลด์ status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"Chat {self.id} - {self.customer.username} @ {self.shop.name if self.shop else '❌ ไม่มีร้าน'}"





class Message(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)  # ✅ เก็บข้อความ
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)  # ✅ รองรับไฟล์รูปภาพ
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30] if self.text else '📷 รูปภาพ'}"
