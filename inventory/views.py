
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout , authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import *

def home(request):
    return render(request, 'list.html')

def list_users(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

def create_user(request):
    if request.method == 'POST':
        username = request.POST['boss']
        password = request.POST['W1234']
        try:
            new_user = User.objects.create_user(username=username, password=password)
            messages.success(request, f"User '{username}' created successfully.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'list.html')

def category_view(request):
    categories = ['หมวดหมู่ที่ 1', 'หมวดหมู่ที่ 2', 'หมวดหมู่ที่ 3', 'หมวดหมู่ที่ 4']
    return render(request, 'list.html', {'categories': categories})

def my_view(request):
    return render(request, 'list.html')

def order_view(request):
    orders = Order.objects.all()
    return render(request, 'order1.html', {'orders': orders})  # เปลี่ยนเป็น order_list.html

# ฟังก์ชันสำหรับแสดงสินค้า
def products(request):
    products = [
        {'name': 'สินค้า A', 'price': 500, 'quantity': 10},
        {'name': 'สินค้า B', 'price': 300, 'quantity': 5}
    ]
    return render(request, 'products.html', {'products': products})

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกคำสั่งซื้อใหม่
            messages.success(request, 'เพิ่มคำสั่งซื้อเรียบร้อยแล้ว')
            return redirect('order_view')  # เปลี่ยนไปที่หน้าแสดงรายการคำสั่งซื้อ
    else:
        form = OrderForm()

    return render(request, 'create_order.html', {'form': form})

def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)  # ค้นหาคำสั่งซื้อที่ต้องการลบ
    order.delete()  # ลบคำสั่งซื้อ
    messages.success(request, 'ลบคำสั่งซื้อเรียบร้อยแล้ว')  # แจ้งข้อความ
    return redirect('order_view')  # กลับไปยังหน้ารายการคำสั่งซื้อ

def other_view(request):
    return render(request, 'order1.html')  # แทนที่ '.html' ด้วยชื่อไฟล์ของคุณ

def homepage(request):
    return render(request, 'homepage.html')

def login(request):
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')  # คืนค่าว่างหากไม่มี key
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            return redirect('homepage')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render(request, 'login.html')




def sales_view(request):
    # ดึงข้อมูลที่เกี่ยวข้องกับฝ่ายขาย
    return render(request, 'sales_view.html')

def status_view(request):
    # ดึงข้อมูลที่เกี่ยวข้องกับสถานะ
    return render(request, 'status_view.html')

def filter_view(request):
    #def order_view(request):
    # ดึงข้อมูลจาก Query Parameters
    status_filter = request.GET.get('status', '')
    sales_channel_filter = request.GET.get('sales_channel', '')

    # กรองคำสั่งซื้อ
    orders = Order.objects.all()

    if status_filter:
        orders = orders.filter(status=status_filter)

    if sales_channel_filter:
        orders = orders.filter(sales_channel=sales_channel_filter)

    return render(request, 'filter_view.html', {'orders': orders})

def update_status(request, order_id):
    # ดึงคำสั่งซื้อที่ต้องการอัปเดต
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        # รับสถานะใหม่จากฟอร์ม
        new_status = request.POST.get('status')

        # อัปเดตสถานะของคำสั่งซื้อ
        if new_status:
            order.status = new_status
            order.save()

        # เปลี่ยนเส้นทางไปยังหน้ารายการคำสั่งซื้อ
        return redirect('order_view')

    return render(request, 'update_status.html', {'order': order})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():  # ตรวจสอบว่ามีอีเมลซ้ำหรือไม่
                    user = User.objects.create_user(username=username, email=email, password=password)
                    Member.objects.create(user=user, extra_info="Default info")
                    messages.success(request, 'การลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ.')
                    return redirect('login')
                else:
                    messages.error(request, 'อีเมลนี้ถูกใช้งานแล้ว')
            else:
                messages.error(request, 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว')
        else:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
    return render(request, 'register.html')