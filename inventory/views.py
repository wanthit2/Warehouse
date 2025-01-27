from .forms import OrderForm, UserProfileForm
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate, login as auth_login, login
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product, Order
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from .forms import UserForm, ProfileForm
from .models import UserProfile

def home1(request):
    return render(request, 'home.html')

def home(request):
    return render(request, 'homepage.html')

def graph_view(request):
    return render(request, 'graph.html')

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

@login_required
def order_view(request):
    if request.user.is_authenticated:  # ตรวจสอบว่าเป็นผู้ใช้ที่ล็อกอิน
        orders = Order.objects.filter(user=request.user)  # ดึงคำสั่งซื้อที่เกี่ยวข้องกับผู้ใช้ที่ล็อกอิน
    else:
        orders = []  # หากผู้ใช้ไม่ได้ล็อกอิน ให้แสดงคำสั่งซื้อเป็นค่าว่าง
    return render(request, 'order1.html', {'orders': orders})

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


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')  # คืนค่าว่างหากไม่มี key
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # ใช้ฟังก์ชัน login ที่มาจาก django.contrib.auth
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            # ตรวจสอบว่า user เป็นแอดมินหรือไม่
            if user.is_staff:
                return redirect('admin_dashboard')  # URL ของหน้าแอดมิน
            else:
                return redirect('home1')  # URL ของหน้าผู้ใช้ทั่วไป
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render(request, 'login.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # ตรวจสอบสิทธิ์ผู้ใช้
            if user.is_staff:
                return redirect('/admin/')
            return redirect('/home1/')
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
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # ตรวจสอบจำนวนสินค้า
        if quantity > product.quantity or quantity <= 0:
            return render(request, 'order_create.html', {
                'product': product,
                'error_message': 'จำนวนสินค้าที่ต้องการสั่งซื้อไม่ถูกต้อง',
            })

        # เก็บจำนวนสินค้าใน session
        request.session['quantity'] = quantity

        # Redirect ไปยังหน้าการยืนยัน
        return redirect('order_confirmation', product_id=product.id)

    return render(request, 'order_create.html', {
        'product': product,
    })

@login_required
def order_confirmation(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Get quantity from session or pass directly in POST request
        quantity = request.session.get('quantity', 1)

        # ตรวจสอบจำนวนสินค้า
        if quantity > product.quantity:
            return render(request, 'order_confirmation.html', {
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity,
                'error_message': 'จำนวนสินค้ามากกว่าที่มีในสต็อก',
            })

        # ลดจำนวนสินค้าคงเหลือในสต็อก
        product.quantity -= quantity
        product.save()

        # สร้างคำสั่งซื้อใหม่ และเชื่อมโยงกับผู้ใช้ที่ล็อกอินอยู่
        Order.objects.create(
            product_name=product.product_name,
            price=product.price,
            quantity=quantity,
            status='pending',  # คำสั่งซื้อที่ยังไม่เสร็จสมบูรณ์
            image=product.image,
            user=request.user,  # เชื่อมโยงกับผู้ใช้งานที่ล็อกอินอยู่
        )

        # Redirect ไปยังหน้าคำสั่งซื้อสำเร็จ
        return redirect('order_success')

    # สำหรับ GET request ให้แสดงหน้า order_confirmation.html
    quantity = request.session.get('quantity', 1)
    return render(request, 'order_confirmation.html', {
        'product': product,
        'quantity': quantity,
        'total_price': product.price * quantity,
    })




def order_success(request):
    return render(request, 'order_success.html')




def order_list(request):
    orders = Order.objects.prefetch_related('items').all()  # ดึงคำสั่งซื้อพร้อมสินค้า
    return render(request, 'order_list.html', {'orders': orders})



@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('create_profile')  # Redirect if profile doesn't exist

    return render(request, 'profile.html', {'profile': user_profile})

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile')  # Redirect to the profile page
    else:
        form = UserProfileForm()

    return render(request, 'create_profile.html', {'form': form})

@login_required
def edit_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # เปลี่ยนเส้นทางไปยังหน้าโปรไฟล์หลังจากบันทึก
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
def profile_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()  # Save profile with the new image if available
            return redirect('profile')  # Redirect to the profile page
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {'form': form, 'user_profile': user_profile})



def cancel_order(request, order_id):
    # ตรวจสอบคำสั่งซื้อที่ต้องการยกเลิก
    order = Order.objects.get(pk=order_id)

    # เปลี่ยนสถานะคำสั่งซื้อเป็นยกเลิก
    order.status = 'ยกเลิก'
    order.save()

    # เปลี่ยนเส้นทางกลับไปยังหน้าแสดงรายการคำสั่งซื้อ
    return redirect('order_view')  # 'order_view' เป็นชื่อ URL ของหน้าคำสั่งซื้อ


@login_required
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง หรือคุณไม่มีสิทธิ์เข้าถึง")

    return redirect('admin_login')

@login_required
def admin_order_list(request):
    orders = Order.objects.prefetch_related('items').all()
    products = Product.objects.all()

    return render(request, 'admin_order_list.html', {'orders': orders, 'products': products})


def admin_orders(request):
    orders = Order.objects.all()  # ดึงข้อมูลคำสั่งซื้อทั้งหมด
    return render(request, 'inventory/admin_orders.html', {'orders': orders})

def edit_order(request, order_id):
    order = Order.objects.get(id=order_id)
    # ฟอร์มการแก้ไขคำสั่งซื้อ
    if request.method == 'POST':
        order.status = request.POST['status']
        order.save()
    return render(request, 'inventory/edit_order.html', {'order': order})

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# หน้าแสดงรายการคำสั่งซื้อ
def admin_orders(request):
    orders = Order.objects.all()
    return render(request, 'admin_orders.html', {'orders': orders})

# ฟังก์ชันเพิ่มคำสั่งซื้อ
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_orders')
    else:
        form = OrderForm()
    return render(request, 'add_order.html', {'form': form})

# ฟังก์ชันแก้ไขคำสั่งซื้อ
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('admin_orders')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form, 'order': order})

# ฟังก์ชันลบคำสั่งซื้อ
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('admin_orders')