from .forms import OrderForm
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404


def home(request):
    return render(request, 'homepage.html')

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
    orders = Order.objects.all()
    return render(request, 'list.html', {'orders': orders})

def order_view(request):
    return render(request, 'order1.html')

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกคำสั่งซื้อใหม่
            messages.success(request, 'เพิ่มคำสั่งซื้อเรียบร้อยแล้ว')
            return redirect('my_view')  # เปลี่ยนไปที่หน้าแสดงรายการคำสั่งซื้อ
    else:
        form = OrderForm()

    return render(request, 'create_order.html', {'form': form})

def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)  # ค้นหาคำสั่งซื้อที่ต้องการลบ
    order.delete()  # ลบคำสั่งซื้อ
    messages.success(request, 'ลบคำสั่งซื้อเรียบร้อยแล้ว')  # แจ้งข้อความ
    return redirect('my_view')  # กลับไปยังหน้ารายการคำสั่งซื้อ

def other_view(request):
    return render(request, 'order1.html')  # แทนที่ '.html' ด้วยชื่อไฟล์ของคุณ

def homepage(request):
    return render(request, 'homepage.html')

def login_page(request):
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')  # คืนค่าว่างหากไม่มี key
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # ใช้ฟังก์ชัน login ที่มาจาก django.contrib.auth
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            return redirect('my_view')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render(request, 'login.html')




def sales_view(request):
    # ดึงข้อมูลที่เกี่ยวข้องกับฝ่ายขาย
    return render(request, 'sales_view.html')

def status_view(request):
    # ดึงข้อมูลที่เกี่ยวข้องกับสถานะ
    return render(request, 'status_view.html')



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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกผู้ใช้ใหม่
            messages.success(request, 'การลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ.')
            return redirect('login')
        else:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


@login_required
def add_product(request):
    if not request.user.is_staff:  # ตรวจสอบสิทธิ์ว่าเป็น Admin
        messages.error(request, 'คุณไม่มีสิทธิ์ในการเพิ่มสินค้า')
        return redirect('product_list')  # เปลี่ยนชื่อ URL เป็นหน้ารายการสินค้า

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มสินค้าสำเร็จ')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})



def products(request):
    products = Product.objects.all()  # ดึงข้อมูลสินค้าทั้งหมด
    return render(request, 'product1.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # รับข้อมูลจากฟอร์ม
        if form.is_valid():
            form.save()  # บันทึกสินค้าในฐานข้อมูล
            return redirect('products')  # กลับไปยังหน้ารายการสินค้า
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


def product_view(request, product_id):
    try:
        # ดึงข้อมูลสินค้าโดยใช้ product_id
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        product = None
    return render(request, 'product_detail.html', {'product': product})

@login_required
def order_create(request, product_id):
    # Retrieve the product by its ID
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Check if a quantity is passed, otherwise default to 1
        quantity = int(request.POST.get('quantity', 1))

        # Create the new order
        new_order = Order.objects.create(
            customer=request.user,  # Use the logged-in user
            items=product.product_name,
            price=product.price,  # Include the price from the product
            quantity=quantity,  # Use the selected quantity
            status='รอดำเนินการ'  # Initial status (Pending)
        )

        # Redirect to the order confirmation page with the order's ID
        return redirect('order_confirmation', order_id=new_order.id)

    # If GET request, display the product details page
    return render(request, 'order_create.html', {'product': product})


def order_confirmation(request, order_id):
    # Retrieve the order with the given order_id
    order = get_object_or_404(Order, pk=order_id)

    # You can also add a success message or flag to indicate the order has been confirmed
    message = "สั่งซื้อแล้ว"

    # Pass the order data and message to the template
    return render(request, 'order_confirmation.html', {'order': order, 'message': message})


def order_list(request):
    orders = Order.objects.all()  # ดึงข้อมูลคำสั่งซื้อทั้งหมดจากฐานข้อมูล
    return render(request, 'order1.html', {'orders': orders})


#ฟังก์ชันการกรองข้อมูลในแถบการค้นหา
def order_list(request):
    query = request.GET.get('q')  # รับค่าค้นหาจากแถบค้นหา
    if query:
        orders = Order.objects.filter(product__icontains=query)  # กรองคำสั่งซื้อที่มีชื่อสินค้าเป็นคำค้น
    else:
        orders = Order.objects.all()
    return render(request, 'order1.html', {'orders': orders})

#ฟังก์ชันสำหรับการกรอง
def order_list(request):
    status_filter = request.GET.get('status')
    if status_filter:
        orders = Order.objects.filter(status=status_filter)
    else:
        orders = Order.objects.all()
    return render(request, 'order1.html', {'orders': orders})
