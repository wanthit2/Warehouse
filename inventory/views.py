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
from .models import Store, Stock
from .forms import StockForm
from .forms import SearchStockForm
from django.contrib.auth.decorators import login_required, user_passes_test




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
    query = request.GET.get('q', '')  # รับค่าค้นหาจาก GET parameter
    products = Product.objects.all()  # ดึงข้อมูลสินค้าทั้งหมด

    # ถ้ามีการค้นหา
    if query:
        products = products.filter(name__icontains=query)  # กรองชื่อสินค้าตามที่ค้นหา

    return render(request, 'list.html', {'products': products, 'query': query})

@login_required
def order_view(request):
    query = request.GET.get('q', '')  # รับค่าค้นหาจาก GET
    orders = Order.objects.filter(user=request.user)  # ดึงคำสั่งซื้อของผู้ใช้ที่ล็อกอิน

    if query:
        orders = orders.filter(product_name__icontains=query)  # ค้นหาคำสั่งซื้อที่มีชื่อสินค้าตรงกับคำค้นหา

    return render(request, 'order1.html', {'orders': orders, 'query': query})

def product_detail_view(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    # Logic for editing the product
    return render(request, 'edit_product.html', {'product': product})


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
                return redirect('home1')  # URL ของหน้าแอดมิน
            else:
                return redirect('home1')  # URL ของหน้าผู้ใช้ทั่วไป
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render(request, 'login.html')


def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # ตรวจสอบข้อมูลผู้ใช้
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # ตรวจสอบสิทธิ์ผู้ใช้ (ถ้าเป็น admin จะไปหน้า /admin/)
            if user.is_staff:
                return redirect('/admin/')
            else:
                # ผู้ใช้ปกติจะไปหน้า /home1/
                return redirect('/home1/')
        else:
            # หากไม่พบผู้ใช้ให้แจ้งข้อผิดพลาด
            messages.error(request, "Username หรือ Password ไม่ถูกต้อง")
            return redirect('login')  # กลับไปที่หน้า login
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

def store_list(request):
    stores = Store.objects.all()
    return render(request, 'store_list.html', {'stores': stores})

# หน้าแสดงสต็อกสินค้าของร้าน
def store_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    stocks = Stock.objects.filter(store=store)
    return render(request, 'store_stock.html', {'store': store, 'stocks': stocks})

# เพิ่มสินค้าในสต็อก
def add_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.store = store  # กำหนดร้านที่สินค้าต้องการเพิ่ม
            stock.save()
            return redirect('store_stock', store_id=store.id)
    else:
        form = StockForm()
    return render(request, 'add_stock.html', {'form': form, 'store': store})

# แก้ไขสต็อกสินค้า
def edit_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('store_stock', store_id=stock.store.id)
    else:
        form = StockForm(instance=stock)
    return render(request, 'edit_stock.html', {'form': form, 'stock': stock})

# ลบสต็อกสินค้า
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    store_id = stock.store.id
    stock.delete()
    return redirect('store_stock', store_id=store_id)


def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)  # กรองสินค้าของร้านนั้นๆ
    return render(request, 'store_detail.html', {'store': store, 'products': products})


def store_list(request):
    stores = Store.objects.all()  # ดึงข้อมูลร้านทั้งหมด
    return render(request, 'store_list.html', {'stores': stores})


@login_required
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'store_list.html', {'stores': stores})

@login_required
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)
    return render(request, 'store_detail.html', {'store': store, 'products': products})



def stock_view(request):
    form = SearchStockForm(request.GET)
    stock_items = Stock.objects.all()

    # ตรวจสอบว่ามีการค้นหาหรือไม่
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            stock_items = stock_items.filter(product_name__icontains=query)  # ใช้การค้นหาที่ไม่สนใจตัวพิมพ์

    return render(request, 'stock.html', {
        'form': form,
        'stock': stock_items
    })

def create_stock(request):
    # คำสั่งหรือการกระทำที่ต้องการทำเมื่อไปยังหน้าสร้างสินค้า
    return render(request, 'create_stock.html')


def update_stock(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        # ค้นหาสินค้าที่ต้องการอัปเดต
        product = Product.objects.get(id=product_id)

        # อัปเดตจำนวนสินค้า
        product.stock_quantity += quantity
        product.save()

        # รีไดเรกต์ไปที่หน้า stock view หรือหน้าอื่น
        return redirect('stock_view')

    # ถ้าเป็น GET request
    return render(request, 'update_stock.html')


def create_product(request):
    # โค้ดสำหรับการสร้างสินค้า
    return render(request, 'create_product.html')


# ฟังก์ชันตรวจสอบว่าเป็น Superuser หรือไม่
def is_admin(user):
    return user.is_superuser

# View สำหรับ Stock ที่เฉพาะ Admin เห็นได้
@login_required
@user_passes_test(is_admin)  # อนุญาตเฉพาะ Admin
def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'inventory/stock.html', {'stocks': stocks})