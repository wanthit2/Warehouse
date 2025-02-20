from django.http import JsonResponse
from .models import ChatSession
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Message
from inventory.models import Product, Shop



def chat_sessions(request):
    if not request.user.is_staff:  # ให้ admin เท่านั้นเข้าถึง
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    sessions = ChatSession.objects.all().values('id', 'customer__username')
    return JsonResponse(list(sessions), safe=False)


@login_required
def customer_chat_view(request, product_id=None):
    """ ฟังก์ชันแสดงหน้าสำหรับแจ้งปัญหาสินค้า """
    product = None
    shop = None

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        shop = product.shop  # ✅ ดึงร้านค้าของสินค้านั้น

    if not shop:
        return JsonResponse({"error": "❌ ไม่สามารถเริ่มแชทได้ ไม่มีร้านค้าเชื่อมโยง"}, status=400)

    chat, created = ChatSession.objects.get_or_create(
        customer=request.user,
        shop=shop  # ✅ บันทึกร้านค้าไปในแชท
    )

    messages = chat.messages.all().order_by("timestamp")  # ✅ ดึงข้อความทั้งหมด
    return render(request, "chat/customer_chat.html", {"chat": chat, "messages": messages, "product": product})


@login_required
def admin_chat_view(request, session_id):
    chat = get_object_or_404(ChatSession, id=session_id)

    # ✅ SuperAdmin สามารถเข้าถึงได้ทุกแชท
    if request.user.is_superuser:
        pass
    else:
        # ✅ ตรวจสอบว่าผู้ใช้เป็นเจ้าของร้านหรือแอดมินร้าน
        if not chat.shop or (request.user not in chat.shop.admins.all() and request.user != chat.shop.owner):
            print(f"❌ {request.user.username} ไม่มีสิทธิ์เข้าถึงแชทนี้")
            return render(request, "chat/forbidden.html")  # ❌ ไม่มีสิทธิ์เข้าถึง

    # ✅ ดึงข้อความทั้งหมด
    messages = chat.messages.all().order_by("timestamp")

    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            Message.objects.create(session=chat, sender=request.user, text=text)

        chat.status = request.POST.get("status", chat.status)
        chat.save()
        return redirect("admin_chat", session_id=session_id)  # ✅ รีเฟรชหน้า

    return render(request, "chat/admin_chat.html", {"chat": chat, "messages": messages})


@login_required
def admin_chat_list_view(request):
    print(f"🛠 Debug: Logged-in User: {request.user} (ID: {request.user.id})")

    if request.user.is_superuser:
        # ✅ SuperAdmin เห็นทุกแชท
        chat_sessions = ChatSession.objects.all().order_by("-created_at")
    else:
        # ✅ ดึงร้านที่ผู้ใช้เป็นเจ้าของหรือเป็นแอดมิน
        owned_shops = Shop.objects.filter(owner=request.user)
        admin_shops = Shop.objects.filter(admins=request.user)

        # ✅ รวมร้านที่เข้าถึงได้
        accessible_shops = owned_shops | admin_shops

        if not accessible_shops.exists():
            print(f"❌ {request.user.username} ไม่มีร้านที่เข้าถึงได้")
            return render(request, "chat/forbidden.html")  # ❌ ไม่มีสิทธิ์เข้าถึง

        # ✅ ดึงแชทที่เกี่ยวข้องกับร้านที่ User ดูแล
        chat_sessions = ChatSession.objects.filter(shop__in=accessible_shops).order_by("-created_at")

    return render(request, "chat/admin_chat_list.html", {"chat_sessions": chat_sessions})





@login_required
def chat_messages_api(request, session_id):
    chat = get_object_or_404(ChatSession, id=session_id)

    # ✅ ดึงข้อความทั้งหมดของแชทนี้
    chat_messages = Message.objects.filter(session=chat).order_by("timestamp")

    messages = [
        {
            "sender": msg.sender.username,
            "message": msg.text,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
        }
        for msg in chat_messages
    ]

    return JsonResponse({"messages": messages})


@login_required
def customer_chat_list_view(request):
    chat_sessions = ChatSession.objects.filter(customer=request.user).order_by("-created_at")  # ✅ แสดงรายการแจ้งปัญหาของลูกค้า

    return render(request, "chat/customer_chat_list.html", {"chat_sessions": chat_sessions})


@login_required
def chat_history_api(request, session_id):
    """ API ดึงประวัติแชทย้อนหลัง """
    chat = get_object_or_404(ChatSession, id=session_id)

    # ✅ ตรวจสอบสิทธิ์ของผู้ใช้
    if request.user.is_superuser or request.user == chat.customer or (chat.shop and (request.user == chat.shop.owner or request.user in chat.shop.admins.all())):
        messages = chat.messages.all().order_by("timestamp")

        message_data = [
            {
                "sender": msg.sender.username,
                "message": msg.text,
                "image": msg.image.url if msg.image else None,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for msg in messages
        ]

        return JsonResponse({"messages": message_data})
    else:
        return JsonResponse({"error": "Forbidden"}, status=403)