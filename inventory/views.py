from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import OrderForm, UserProfileForm, CustomUserCreationForm
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
from inventory.models import CustomUser
from .forms import ShopOwnerRequestForm
from .forms import CustomUserProfileForm
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse, HttpResponse
from inventory.models import Shop


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
        products = products.filter(product_name__icontains=query)  # กรองชื่อสินค้าตามที่ค้นหา

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

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail_view', pk=product.pk)  # ไปที่หน้ารายละเอียดของสินค้า
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})


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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # ตรวจสอบข้อมูลผู้ใช้
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # ล็อกอินเข้า session
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')

            # ถ้าเป็น superuser (superadmin) ให้ไปที่ /admin/
            if user.is_superuser:
                return redirect('/admin_home/')
            else:
                return redirect('home1')  # ผู้ใช้ทั่วไปไปที่ home1

        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')

    return render(request, 'login.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # ตรวจสอบข้อมูลผู้ใช้ (ยืนยันตัวตน)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ตรวจสอบสิทธิ์ผู้ใช้
            if user.is_superuser:  # ถ้าเป็น superadmin ไปที่ /admin/
                return redirect('/admin/')
            elif user.is_staff:  # ถ้าเป็น staff ธรรมดา ไปที่หน้า admin
                return redirect('/staff-dashboard/')
            else:
                return redirect('/home1/')  # ผู้ใช้ทั่วไปไปหน้า home1

        else:
            messages.error(request, "Username หรือ Password ไม่ถูกต้อง")
            return redirect('login')  # กลับไปที่หน้า login

    return render(request, 'login.html')

def sales_view(request):
    # ดึงข้อมูลที่เกี่ยวข้องกับฝ่ายขาย
    return render(request, 'sales_view.html')


@login_required
def status_view(request):
    # ดึงข้อมูลผู้ใช้ที่ล็อกอินอยู่
    user = request.user

    # ดึงข้อมูลร้านของผู้ใช้ ถ้ามีร้าน
    shop = None
    try:
        shop = Shop.objects.get(owner=user)  # ถ้าผู้ใช้มีร้าน
    except Shop.DoesNotExist:
        shop = None  # ถ้าไม่มีร้าน

    return render(request, 'status_view.html', {'user': user, 'shop': shop})



@login_required
def update_status(request, order_id):
    # ดึงคำสั่งซื้อที่ต้องการอัปเดต
    order = get_object_or_404(Order, order_id=order_id)

    # ตรวจสอบสิทธิ์ของผู้ใช้
    if order.shop.owner != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ในการอัปเดตสถานะคำสั่งซื้อนี้")

    if request.method == 'POST':
        # รับสถานะใหม่จากฟอร์ม
        new_status = request.POST.get('status')

        # อัปเดตสถานะของคำสั่งซื้อ
        if new_status:
            order.status = new_status
            order.save()

            # แสดงข้อความแจ้งเตือน
            messages.success(request, f'สถานะของคำสั่งซื้อ {order.order_id} ได้รับการอัปเดตแล้ว!')

        # เปลี่ยนเส้นทางไปยังหน้ารายการคำสั่งซื้อ
        return redirect('order_view')

    # ส่งข้อมูลคำสั่งซื้อและชื่อร้านไปยังเทมเพลต
    return render(request, 'update_status.html', {
        'order': order,
        'shop_name': order.shop.name,  # แสดงชื่อร้านที่เชื่อมโยงกับคำสั่งซื้อ
    })


def shop_owner_status(request):
    user = request.user  # รับข้อมูลผู้ใช้ที่ล็อกอิน

    try:
        # ดึงข้อมูลร้านค้าที่เชื่อมโยงกับผู้ใช้
        shop = Shop.objects.get(owner=user)
    except Shop.DoesNotExist:
        shop = None  # ถ้าผู้ใช้ไม่มีร้านก็ให้ shop เป็น None

    return render(request, 'status_request.html', {
        'user': user,
        'shop': shop,  # ส่งข้อมูลร้านไปยังเทมเพลต
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            if not username:  # ตรวจสอบว่า username ไม่เป็นค่าว่าง
                form.add_error('username', 'Username cannot be empty')
            else:
                user.set_password(form.cleaned_data['password1'])
                user.save()
                messages.success(request, 'การลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ.')
                return redirect('login')
        else:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})




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




@login_required
def create_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            # เชื่อมโยงสินค้ากับร้านของผู้ใช้ที่เข้าสู่ระบบ
            stock.store = request.user.stores.first()
            stock.save()
            return redirect('stock_view')
    else:
        form = StockForm()

    return render(request, 'create_stock.html', {'form': form})


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







from django.db.models import Q
@login_required
def admin_home_view(request):
    # ตรวจสอบว่าเป็น superuser
    if request.user.is_superuser:
        # ดึงทุกร้านและแอดมินของร้าน
        shops = Shop.objects.all()  # ดึงทุกร้าน
        admins_by_shop = {}

        # สร้าง dictionary ที่เก็บแอดมินของแต่ละร้าน
        for shop in shops:
            admins = shop.admins.all()  # ค้นหาแอดมินที่มีสิทธิ์ในร้านนี้
            admins_by_shop[shop] = admins

        # ส่งข้อมูลร้านและแอดมินให้ template
        return render(request, 'admin_home.html', {'admins_by_shop': admins_by_shop})

    # debug ตรวจสอบค่าของ user
    print("User type:", request.user.user_type)
    print("Is shop owner approved:", request.user.is_shop_owner_approved)

    # ตรวจสอบว่า user เป็นเจ้าของร้านหรือแอดมินร้าน
    if request.user.is_shop_owner_approved and request.user.user_type in ['shop_owner', 'shop_admin']:
        try:
            # ค้นหาร้านที่ผู้ใช้เป็นเจ้าของหรือแอดมิน
            shop = Shop.objects.filter(owner=request.user).first()

            # ถ้าไม่พบร้าน
            if not shop:
                # ตรวจสอบว่า user เป็นแอดมินของร้านใดร้านหนึ่ง
                shop = Shop.objects.filter(admins=request.user).first()

            # debug ข้อมูลร้านที่ค้นพบ
            if shop:
                print("Found shop:", shop.name)
                return render(request, 'admin_homeshop.html', {'shop': shop})
            else:
                return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")

        except Shop.DoesNotExist:
            return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")

    # ถ้าไม่ใช่เจ้าของร้านที่ได้รับการอนุมัติหรือแอดมินร้าน
    return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")





def manage_users(request):
    users = CustomUser.objects.filter(is_shop_owner_approved=False)
    return render(request, 'admin_manage_users.html', {'users': users})



# ตัวอย่างการอนุมัติผู้ใช้งาน
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # เปลี่ยนประเภทผู้ใช้เป็นเจ้าของร้านและเปลี่ยนสถานะ
    user.user_type = 'shop_owner'
    user.is_shop_owner_approved = True
    user.is_shop_owner = True  # เพิ่มสถานะเป็นเจ้าของร้าน
    user.save()

    # สร้างร้านใหม่ให้เจ้าของร้าน (ถ้ายังไม่มี)
    store, created = Store.objects.get_or_create(name=f"ร้านของ {user.username}", owner=user)

    # เชื่อมโยงร้านกับผู้ใช้ (ถ้ามีระบบ ManyToMany)
    if hasattr(user, 'stores'):
        user.stores.add(store)

    # แจ้งเตือน
    messages.success(request, f'ผู้ใช้ {user.username} ได้รับการอนุมัติให้เป็นเจ้าของร้านและร้านถูกสร้างแล้ว!')
    return redirect('manage_users')


@login_required
def admin_home_shop(request):
    # ดึงร้านที่เจ้าของเป็นผู้ใช้ที่ล็อกอิน
    shop = get_object_or_404(Shop, owner=request.user)

    # ส่งข้อมูลร้านไปยังเทมเพลต
    return render(request, "admin_homeshop.html", {'shop': shop})



def request_status(request, user_id):
    # ดึงข้อมูลผู้ใช้จากฐานข้อมูล
    user = get_object_or_404(CustomUser, id=user_id)

    # ส่งข้อมูลผู้ใช้และสถานะคำขอไปยัง template
    return render(request, 'request_status.html', {'user': user})



def reject_user(request, user_id):
    # ดึงผู้ใช้จากฐานข้อมูล
    user = get_object_or_404(CustomUser, id=user_id)

    # ปรับสถานะของผู้ใช้ที่ถูกปฏิเสธ
    user.is_shop_owner_requested = False  # หรือสถานะที่ต้องการให้เป็นเมื่อปฏิเสธ
    user.save()

    # แสดงข้อความแจ้งเตือน
    messages.success(request, 'ผู้ใช้ถูกปฏิเสธเรียบร้อยแล้ว')

    return redirect('manage_users')  # หรือไปที่หน้าที่ต้องการ



def request_shop_owner(request):
    if request.method == 'POST':
        form = ShopOwnerRequestForm(request.POST)
        if form.is_valid():
            shop_request = form.save(commit=False)  # ไม่บันทึกทันที
            shop_request.is_approved = False  # ตั้งค่าเริ่มต้นเป็น False
            shop_request.save()  # บันทึกคำขอ
            return redirect('shop-owner-request-success')
    else:
        form = ShopOwnerRequestForm()
    return render(request, 'request_shop_owner.html', {'form': form})

def success_page(request):
    return render(request, 'success.html')


def shop_owner_request(request):
    # logic สำหรับการขอเป็นเจ้าของร้าน
    if request.method == 'POST':
        # บันทึกข้อมูลหรือทำการอนุมัติ
        return redirect('shop-owner-request-success')  # ใช้ URL นี้หลังจาก POST เสร็จ
    return render(request, 'shop_owner_request.html')


def shop_owner_request_success(request):
    return render(request, 'shop_owner_request_success.html')


from .forms import AddAdminForm
def add_admin(request):
    if request.method == 'POST':
        form = AddAdminForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            # เพิ่มสิทธิ์เป็นแอดมิน
            user.is_staff = True
            user.save()
            messages.success(request, f"ผู้ใช้ {user.username} ได้รับสิทธิ์เป็นแอดมินแล้ว")
            return redirect('add_admin')  # ไปที่หน้าจัดการผู้ใช้งาน
    else:
        form = AddAdminForm()

    return render(request, 'add_admin.html', {'form': form})


def manage_shops(request):
    query = request.GET.get('q', '')

    # กรณีเป็น Superuser ให้เห็นทุกร้าน
    if request.user.is_superuser:
        shops = Shop.objects.filter(name__icontains=query) if query else Shop.objects.all()

    # กรณีเป็น Staff (Admin ร้านค้า) ให้เห็นเฉพาะร้านที่ตนเองเป็นเจ้าของ
    elif request.user.is_staff:
        shops = Shop.objects.filter(owner=request.user, name__icontains=query) if query else Shop.objects.filter(
            owner=request.user)

    # กรณีเป็นผู้ใช้ทั่วไป ให้เห็นเฉพาะร้านที่ตัวเองเป็นเจ้าของ
    else:
        shops = Shop.objects.filter(owner=request.user, name__icontains=query) if query else Shop.objects.filter(
            owner=request.user)

    return render(request, 'manage_shops.html', {'shops': shops, 'query': query})



from .forms import ShopForm
def add_shop(request):
    if request.method == "POST":
        form = ShopForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_shops')
    else:
        form = ShopForm()
    return render(request, 'shop_form.html', {'form': form})

def edit_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == "POST":
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('manage_shops')
    else:
        form = ShopForm(instance=shop)
    return render(request, 'shop_form.html', {'form': form})

def delete_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    shop.delete()
    return redirect('manage_shops')


def shop_detail(request, shop_id):
    # ดึงข้อมูลร้านค้าตาม ID
    shop = get_object_or_404(CustomUser, pk=shop_id)
    return render(request, 'shop_detail.html', {'shop': shop})


def product_list(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)  # ใช้ get_object_or_404 เพื่อหลีกเลี่ยงข้อผิดพลาด
    products = Product.objects.filter(shop=shop)
    return render(request, 'product_list.html', {'shop': shop, 'products': products})

def add_product(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list', shop_id=shop.id)
    else:
        form = ProductForm(initial={'shop': shop})
    return render(request, 'add_product.html', {'form': form, 'shop': shop})


def is_shop_owner(user):
    return user.is_shop_owner

def shop_owner_request_success(request):
    return render(request, 'shop_owner_request_success.html')




def add_shop(request):
    if request.method == "POST":
        name = request.POST.get("name")
        owner_username = request.POST.get("owner")  # รับ username จากฟอร์ม
        owner = User.objects.get(username=owner_username)  # แปลงเป็น User object
        Shop.objects.create(name=name, owner=owner)
        return redirect("shop_list")

    return render(request, "add_shop.html")


# ฟังก์ชันแก้ไขร้านค้า
def edit_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == "POST":
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('manage_shops')
    else:
        form = ShopForm(instance=shop)

    return render(request, 'edit_shop.html', {'form': form, 'shop': shop})

# ฟังก์ชันลบร้านค้า
def delete_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    shop.delete()
    return redirect('manage_shops')


class AddShopView(CreateView):
    model = Shop
    fields = ['name', 'owner', 'location']
    template_name = 'add_shop.html'
    success_url = reverse_lazy('shop_list')  # ส่งกลับไปหน้ารายการร้านค้า



def shop_list(request):
    shops = Shop.objects.all()  # ดึงร้านค้าทั้งหมด
    return render(request, 'shop_list.html', {'shops': shops})


@login_required
def create_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user  # กำหนดเจ้าของให้เป็นผู้ใช้ที่ล็อกอิน
            shop.save()  # บันทึกข้อมูลร้าน
            return redirect('manage_shop_admins', shop_id=shop.id)  # ส่ง shop.id ไปยัง URL
    else:
        form = ShopForm()

    return render(request, 'create_shop.html', {'form': form})


@login_required
def stock_view(request):
    print(f"User: {request.user}, is_admin: {request.user.is_admin}, is_shop_owner: {request.user.is_shop_owner}")

    if request.user.is_admin:
        products = Product.objects.all()
    elif request.user.is_shop_owner:
        products = Product.objects.filter(shop__owner=request.user)
    else:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")

    return render(request, 'stock_view.html', {'products': products})


# ฟังก์ชันเพิ่มสต็อก
def stock_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()  # เพิ่มสินค้าใหม่
            return redirect('stock_view')  # เปลี่ยนไปยังหน้ารายการสินค้า
    else:
        form = ProductForm()

    return render(request, 'stock_add.html', {'form': form})


# ฟังก์ชันแก้ไขสินค้า
def stock_edit(request, id):
    product = get_object_or_404(Product, pk=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()  # บันทึกการแก้ไข
            return redirect('stock_view')
    else:
        form = ProductForm(instance=product)

    return render(request, 'stock_edit.html', {'form': form, 'product': product})


# ฟังก์ชันลบสินค้า
def stock_delete(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.method == 'POST':
        product.delete()  # ลบสินค้า
        return redirect('stock_view')
    return render(request, 'stock_delete_confirm.html', {'product': product})


@login_required
def manage_shop_admins(request, shop_id):
    # ดึงข้อมูลร้านที่มี shop_id
    shop = get_object_or_404(Shop, id=shop_id)

    # ดึงข้อมูลแอดมินของร้าน
    admins = shop.admins.all()  # สมมติว่า Shop มีฟิลด์ admins ที่เชื่อมโยงกับผู้ใช้ (CustomUser)

    # ดึงข้อมูลผู้ใช้ทั้งหมด
    all_users = CustomUser.objects.all()

    # การจัดการการเพิ่มหรือลบแอดมิน
    if request.method == "POST":
        if 'add_admin' in request.POST:
            admin_id = request.POST.get("admin_id")
            admin_user = CustomUser.objects.get(id=admin_id)
            shop.admins.add(admin_user)  # เพิ่มแอดมินให้กับร้าน
            messages.success(request, f"เพิ่มแอดมิน {admin_user.username} แล้ว")
        elif 'remove_admin' in request.POST:
            admin_id = request.POST.get("admin_id")
            admin_user = CustomUser.objects.get(id=admin_id)
            shop.admins.remove(admin_user)  # ลบแอดมินออกจากร้าน
            messages.success(request, f"ลบแอดมิน {admin_user.username} แล้ว")

    context = {
        'shop': shop,
        'admins': admins,
        'all_users': all_users,
    }

    return render(request, "manage_shop_admins.html", context)



@login_required
def manage_products(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)

    if request.user != shop.owner:
        return redirect('home')

    products = shop.products.all()

    # เพิ่มสินค้า
    if request.method == 'POST' and 'add_product' in request.POST:
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.shop = shop  # กำหนดให้สินค้าเชื่อมโยงกับร้านนี้
            new_product.save()
            return redirect('manage_products', shop_id=shop.id)

    # ลบสินค้า
    if request.method == 'POST' and 'delete_product' in request.POST:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        if product.shop == shop:
            product.delete()
        return redirect('manage_products', shop_id=shop.id)

    # แก้ไขสินค้า
    if request.method == 'POST' and 'edit_product' in request.POST:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products', shop_id=shop.id)

    form = ProductForm()  # สำหรับการเพิ่มสินค้าใหม่
    context = {
        'shop': shop,
        'products': products,
        'form': form,
    }

    return render(request, 'manage_products.html', context)









