from .forms import OrderForm
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product, Order
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from .forms import UserForm, ProfileForm





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

def order_view(request):
    orders = Order.objects.all()
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

        # สร้างคำสั่งซื้อใหม่
        Order.objects.create(
            product_name=product.product_name,
            price=product.price,
            quantity=quantity,
            status='pending',  # Pending order
            image=product.image,
        )

        # Redirect to success page
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
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        if profile:
            form = ProfileForm(request.POST, instance=profile)
        else:
            form = ProfileForm(request.POST)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile')  # กลับมาที่หน้าชื่อโปรไฟล์

    else:
        if profile:
            form = ProfileForm(instance=profile)
        else:
            form = ProfileForm()

    return render(request, 'profile.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'inventory/profile.html', context)





def cancel_order(request, order_id):
    # ตรวจสอบคำสั่งซื้อที่ต้องการยกเลิก
    order = Order.objects.get(pk=order_id)

    # เปลี่ยนสถานะคำสั่งซื้อเป็นยกเลิก
    order.status = 'ยกเลิก'
    order.save()

    # เปลี่ยนเส้นทางกลับไปยังหน้าแสดงรายการคำสั่งซื้อ
    return redirect('order_view')  # 'order_view' เป็นชื่อ URL ของหน้าคำสั่งซื้อ