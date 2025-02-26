
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
from .forms import UserForm, UserProfileForm  # ✅ ใช้ UserProfileForm แทน ProfileForm

from .models import UserProfile
from .models import Stock
from .forms import StockForm
from .forms import SearchStockForm
from django.contrib.auth.decorators import login_required, user_passes_test
from inventory.models import CustomUser
from .forms import ShopOwnerRequestForm
from .forms import CustomUserProfileForm
from django.http import HttpResponseForbidden, HttpResponseNotFound, JsonResponse, HttpResponse
from inventory.models import Shop
from .models import Product, Category, Supplier
import urllib, base64
import matplotlib.pyplot as plt
import io
from django.db.models import Sum, Count, F
import calendar

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce





def home1(request):
    return render(request, 'home.html')

def home(request):
    return render(request, 'homepage.html')



import json
def user_is_shop_owner(user):
    return Shop.objects.filter(owner=user).exists()

@login_required
def graph_view(request):
    # 🔹 ตรวจสอบว่า user เป็นเจ้าของร้านหรือไม่
    if not user_is_shop_owner(request.user):
        return redirect('home1')  # 🔥 เปลี่ยนเส้นทางหากไม่ใช่เจ้าของร้าน

    # 🔹 ดึงร้านค้าที่ผู้ใช้เป็นเจ้าของ
    shop = Shop.objects.filter(owner=request.user).first()

    if not shop:
        return render(request, 'graph.html', {'error_message': "คุณไม่มีร้านค้า"})

    # 🔹 คำนวณสถิติเฉพาะร้านนี้
    total_products = Product.objects.filter(shop=shop).count()
    total_categories = Category.objects.filter(product__shop=shop).distinct().count()
    total_suppliers = Supplier.objects.count()
    total_orders = Order.objects.filter(shop=shop).count()

    # 🔹 **แก้ไขการคำนวณรายได้ ให้รวมเฉพาะออเดอร์ที่ไม่ถูกยกเลิก**
    total_revenue = Order.objects.filter(shop=shop).exclude(status="ยกเลิก").aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0  # 🔥 รวมเฉพาะคำสั่งซื้อที่ไม่ถูกยกเลิก

    # 🔹 ดึงข้อมูลคำสั่งซื้อรายเดือน (เฉพาะร้านนี้)
    orders_by_month = (
        Order.objects.filter(shop=shop).exclude(status="ยกเลิก")  # 🔥 ไม่รวมออเดอร์ที่ถูกยกเลิก
        .values_list('created_at__month')
        .annotate(
            total_orders=Count('order_id'),
            total_revenue=Sum(F('price') * F('quantity'))
        )
    )

    # 🔹 แปลงข้อมูลให้ใช้ในกราฟ Chart.js
    months = [calendar.month_abbr[month[0]] for month in orders_by_month]
    order_counts = [month[1] for month in orders_by_month]
    revenues = [float(month[2] or 0) for month in orders_by_month]  # 🔥 แปลง Decimal เป็น float

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),  # 🔥 แปลง Decimal เป็น float
        'order_labels': json.dumps(months),
        'order_data': json.dumps(order_counts),
        'revenue_labels': json.dumps(months),
        'revenue_data': json.dumps(revenues),
        'shop_name': shop.name,
    }
    return render(request, 'graph.html', context)



@login_required
def cancel_order(request, order_id):
    order = Order.objects.filter(order_id=order_id, shop__owner=request.user).first()

    if order and order.status != "ยกเลิก":  # 🔥 ตรวจสอบเป็น "ยกเลิก" แทน 'cancelled'
        # 🔹 คำนวณจำนวนเงินที่ต้องลดลงก่อนเปลี่ยนสถานะ
        order_total = order.price * order.quantity

        # 🔹 เปลี่ยนสถานะเป็น "ยกเลิก"
        order.status = "ยกเลิก"
        order.save()

        # 🔹 คำนวณรายได้ใหม่หลังจากออเดอร์ถูกยกเลิก
        shop = order.shop
        total_revenue = Order.objects.filter(shop=shop).exclude(status="ยกเลิก").aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0  # 🔥 รวมเฉพาะออเดอร์ที่ยังไม่นับว่ายกเลิก

        # 🔹 บันทึกยอดเงินใหม่ในร้าน
        shop.total_revenue = total_revenue
        shop.save()

    return redirect('graph_view')




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
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    # ✅ ตรวจสอบว่าผู้ใช้ล็อกอินอยู่หรือไม่
    if not request.user.is_authenticated:
        return render(request, 'list.html', {
            'products': [],
            'query': query,
            'categories': Category.objects.all(),
            'selected_category': category_filter,
            'selected_status': status_filter,
        })

    # ✅ ถ้าผู้ใช้เป็นเจ้าของร้าน ให้เห็นสินค้าของร้านตัวเอง
    if request.user.is_shop_owner:
        products = Product.objects.filter(shop__owner=request.user)

    # ✅ ถ้าผู้ใช้เป็น Admin ร้าน ให้เห็นสินค้าของร้านที่ตนเป็นแอดมิน
    elif request.user.is_shop_admin:
        shops = Shop.objects.filter(admins=request.user)  # ดึงร้านที่ user เป็นแอดมิน
        products = Product.objects.filter(shop__in=shops)  # ดึงสินค้าของร้านที่เป็นแอดมิน

    else:
        products = Product.objects.none()  # ❌ ไม่ใช่เจ้าของร้านหรือแอดมินร้าน → ไม่เห็นอะไรเลย

    # ✅ ป้องกันค่า None โดยใช้ Coalesce
    products = products.annotate(
        total_stock=Coalesce(Sum('stock__quantity'), Value(0))
    )

    # ✅ กรองตามเงื่อนไขการค้นหา
    if query:
        products = products.filter(product_name__icontains=query)
    if category_filter:
        products = products.filter(category__id=category_filter)
    if status_filter:
        products = products.filter(status=status_filter)

    return render(request, 'list.html', {
        'products': products,
        'query': query,
        'categories': Category.objects.all(),
        'selected_category': category_filter,
        'selected_status': status_filter,
    })


@login_required
def order_view(request):
    query = request.GET.get('q', '')

    # ✅ ดึงข้อมูล Order พร้อมกับข้อมูลร้านค้า (shop) และสินค้า (product)
    orders = Order.objects.select_related('shop', 'product').filter(user=request.user)

    # ✅ กรองตามชื่อสินค้า (ใช้ product.product_name)
    if query:
        orders = orders.filter(product__product_name__icontains=query)

    return render(request, 'order1.html', {'orders': orders, 'query': query})


def product_detail_view(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products')  # แก้ไขให้ตรงกับ URL ของหน้าจัดการสินค้า
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})


def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, product=product)
        if form.is_valid():
            form.save()
            return redirect('order_view')
    else:
        form = OrderForm(product=product)

    return render(request, 'create_order.html', {'form': form, 'product': product})


def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)  # ค้นหาคำสั่งซื้อที่ต้องการลบ
    order.delete()  # ลบคำสั่งซื้อ
    messages.success(request, 'ลบคำสั่งซื้อเรียบร้อยแล้ว')  # แจ้งข้อความ
    return redirect('my_view')  # กลับไปยังหน้ารายการคำสั่งซื้อ


User = get_user_model()
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        try:
            user = User.objects.get(email=email)  # ค้นหาผู้ใช้จากอีเมล
            user = authenticate(request, username=user.username, password=password)  # ใช้ username ที่ผูกกับอีเมล
        except User.DoesNotExist:
            user = None

        if user is not None:
            auth_login(request, user)
            messages.success(request, "เข้าสู่ระบบสำเร็จ")

            if user.is_superuser:
                return redirect("/admin_home/")
            else:
                return redirect("home1")  # ผู้ใช้ทั่วไปไปที่ home1
        else:
            messages.error(request, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")

    return render(request, "login.html")

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
    products = Product.objects.select_related('shop').all()  # ✅ ดึงสินค้าพร้อมร้านค้า
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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Product

@login_required
def order_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity > product.quantity or quantity <= 0:
            return render(request, 'order_create.html', {
                'product': product,
                'error_message': 'จำนวนสินค้าที่ต้องการสั่งซื้อไม่ถูกต้อง',
            })

        # ✅ ลดสต๊อกสินค้า
        product.quantity -= quantity
        product.save()

        # ✅ สร้างคำสั่งซื้อ พร้อมบันทึก `product`
        Order.objects.create(
            product=product,  # ✅ ใช้ ForeignKey product
            price=product.price,
            quantity=quantity,
            status='pending',
            image=product.image,
            user=request.user,
            shop=product.shop,
        )

        return redirect('order_success')

    return render(request, 'order_create.html', {'product': product})




@login_required
def order_confirmation(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity = request.session.get('quantity', 1)
        shop = product.shop if hasattr(product, 'shop') else None

        # ✅ บันทึกคำสั่งซื้อโดยใช้ ForeignKey
        order = Order.objects.create(
            product=product,  # ✅ ใช้ ForeignKey แทน String
            price=product.price,
            quantity=quantity,
            status='pending',
            image=product.image,
            user=request.user,
            shop=shop,
        )

        # ✅ ลดสต๊อกสินค้า
        stock = Stock.objects.filter(product=product).first()
        if stock:
            if stock.quantity >= quantity:
                stock.quantity -= quantity
                stock.save()
                print(f"✅ อัปเดตสต๊อกสำเร็จ! คงเหลือ: {stock.quantity} ชิ้น")
            else:
                print(f"⚠️ สินค้า {product.product_name} ไม่เพียงพอในสต๊อก!")
        else:
            print(f"⚠️ ไม่พบสินค้า {product.product_name} ในสต๊อก!")

        return redirect('order_success')

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
def admin_order_list(request):
    # รับค่าตัวกรอง `status` จาก URL (GET Parameter)
    status = request.GET.get('status', None)

    if request.user.is_superuser:
        # ถ้าเป็น SuperAdmin ให้เห็นคำสั่งซื้อทั้งหมด
        orders = Order.objects.all()
    else:
        # ดึงร้านที่ผู้ใช้เป็นเจ้าของหรือเป็นแอดมิน
        owned_shops = Shop.objects.filter(owner=request.user).values_list('id', flat=True)
        managed_shops = Shop.objects.filter(admins=request.user).values_list('id', flat=True)


        # รวมร้านที่ผู้ใช้เกี่ยวข้อง
        related_shop_ids = list(owned_shops) + list(managed_shops)


        # กรองเฉพาะคำสั่งซื้อที่เกี่ยวข้องกับร้านของผู้ใช้
        orders = Order.objects.filter(
            Q(shop_id__in=related_shop_ids)
        ).distinct()

    # ถ้ามีการส่ง `status` ให้กรองเฉพาะคำสั่งซื้อนั้น
    if status:
        orders = orders.filter(status=status)

    return render(request, 'admin_order_list.html', {'orders': orders})


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)  # 🔥 ใช้ order_id แทน id

    # ตรวจสอบสิทธิ์ของเจ้าของร้าน
    if request.user != order.shop.owner and not request.user.is_superuser:
        return render(request, 'order_list.html', {'error_message': "คุณไม่มีสิทธิ์แก้ไขคำสั่งซื้อนี้"})

    if request.method == "POST":
        new_status = request.POST.get("status")

        # ถ้าคำสั่งซื้อถูกยกเลิก ต้องลดรายได้ของร้าน
        if new_status == "cancelled" and order.status != "cancelled":
            shop = order.shop
            total_revenue = Order.objects.filter(shop=shop, status='shipped').aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0

            # 🔹 บันทึกยอดเงินใหม่ในร้าน
            shop.total_revenue = total_revenue
            shop.save()

        # อัปเดตสถานะคำสั่งซื้อ
        order.status = new_status
        order.save()

    return redirect('admin_order_list')




@login_required
def admin_delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('admin_order_list')

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            request.user.username = form.cleaned_data.get('username', request.user.username)
            request.user.email = form.cleaned_data.get('email', request.user.email)
            request.user.save()
            messages.success(request, "อัปเดตโปรไฟล์เรียบร้อยแล้ว!")
            return redirect('profile')

    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {'form': form, 'profile': user_profile})


@login_required
def create_profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)  # หยุดก่อนบันทึกลง DB
            profile.user = request.user  # กำหนด user
            profile.save()
            messages.success(request, "โปรไฟล์ถูกสร้างเรียบร้อยแล้ว!")
            return redirect("profile")

        else:
            messages.error(request, "เกิดข้อผิดพลาด! กรุณาตรวจสอบข้อมูลของคุณ.")

    else:
        form = UserProfileForm()

    return render(request, "create_profile.html", {"form": form})


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)  # หยุดก่อนบันทึกลง DB
            profile.user = request.user  # กำหนด user ก่อนบันทึก
            profile.save()
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return redirect('profile')  # กลับไปที่หน้าโปรไฟล์
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'edit_profile.html', {'form': form})







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
    orders = Order.objects.select_related('shop').all()
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


@login_required
def create_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.shop = request.user.owned_shops.first()
            if stock.shop:  # ตรวจสอบว่าผู้ใช้มีร้านค้าหรือไม่
                stock.save()
                return redirect('stock_view')
            else:
                form.add_error(None, "คุณไม่มีร้านค้า กรุณาสร้างร้านค้าก่อน")

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


def manage_users(request):
    users = CustomUser.objects.filter(is_shop_owner_approved=False)
    return render(request, 'admin_manage_users.html', {'users': users})



# ตัวอย่างการอนุมัติผู้ใช้งาน
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # ✅ เปลี่ยนประเภทผู้ใช้เป็นเจ้าของร้านและเปลี่ยนสถานะ
    user.user_type = 'shop_owner'
    user.is_shop_owner_approved = True
    user.is_shop_owner = True  # เพิ่มสถานะเป็นเจ้าของร้าน
    user.save()

    # ✅ สร้างร้านใหม่ให้เจ้าของร้าน (ถ้ายังไม่มี)
    shop, created = Shop.objects.get_or_create(name=f"ร้านของ {user.username}", owner=user)

    # ✅ เชื่อมโยงร้านกับผู้ใช้ (ถ้ามีระบบ ManyToMany)
    if hasattr(user, 'owned_shops'):  # ใช้ related_name="owned_shops" ใน Shop
        user.owned_shops.add(shop)

    # ✅ แจ้งเตือน
    messages.success(request, f'ผู้ใช้ {user.username} ได้รับการอนุมัติให้เป็นเจ้าของร้านและร้านถูกสร้างแล้ว!')
    return redirect('manage_users')


@login_required
def admin_home_shop(request):
    try:
        # ค้นหาร้านที่ผู้ใช้เป็นเจ้าของ
        shop = Shop.objects.filter(owner=request.user).first()

        if not shop:
            # ค้นหาว่าผู้ใช้เป็นแอดมินของร้านไหน
            shop = Shop.objects.filter(admins=request.user).first()

        # ให้ทุกคนที่มีร้านสามารถเข้าถึงได้
        if shop:
            return render(request, 'admin_homeshop.html', {'shop': shop})

        # ถ้าไม่พบร้านให้แสดงข้อความ
        return render(request, 'admin_homeshop.html', {})  # กรณีไม่มีร้านก็ให้แสดงหน้า

    except Shop.DoesNotExist:
        return render(request, 'admin_homeshop.html', {})  # กรณีไม่มีร้านให้แสดงหน้า



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
    if request.method == 'POST':
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('manage_shops')  # หรือเปลี่ยนเป็นหน้าที่ต้องการให้ไปหลังแก้ไข
    else:
        form = ShopForm(instance=shop)

    return render(request, 'edit_shop.html', {'form': form, 'shop': shop})

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


from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import Product


LOW_STOCK_THRESHOLD = 5  # 🔥 กำหนดค่าขั้นต่ำที่ถือว่าสินค้าใกล้หมด

def stock_view(request):
    # ✅ ตรวจสอบว่าผู้ใช้ล็อกอินหรือไม่
    if not request.user.is_authenticated:
        return HttpResponseForbidden("คุณต้องเข้าสู่ระบบก่อน")

    # ✅ ดึงข้อมูลจาก `Stock` โดยรวมจำนวนสินค้าของแต่ละ `Product`
    if request.user.is_superuser:
        stocks = Stock.objects.select_related("product", "shop").all()

    elif request.user.owned_shops.exists():
        stocks = Stock.objects.filter(shop__owner=request.user).select_related("product", "shop")

    elif request.user.admin_shops.exists():
        stocks = Stock.objects.filter(shop__admins=request.user).select_related("product", "shop")

    else:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")

        # ✅ รับค่าจากฟอร์มค้นหา
    search_query = request.GET.get('search', '').strip()
    if search_query:
        stocks = stocks.filter(
            Q(product__product_name__icontains=search_query) |  # ✅ ค้นหาจากชื่อสินค้า
            Q(product__category__name__icontains=search_query)  # ✅ ค้นหาจากหมวดหมู่สินค้า
        )

    # ✅ ค้นหาสินค้าที่เหลือน้อย
    low_stock_products = stocks.filter(quantity__lte=LOW_STOCK_THRESHOLD)

    return render(request, 'stock_view.html', {
        'stocks': stocks,
        'low_stock_products': low_stock_products,
    })


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
    shop = get_object_or_404(Shop, id=shop_id)

    # ดึงแอดมินของร้านนี้
    admins = shop.admins.all()

    # ดึงผู้ใช้ที่ยังไม่เป็นแอดมินร้านนี้
    all_users = CustomUser.objects.exclude(id__in=admins.values_list('id', flat=True))

    if request.method == "POST":
        admin_id = request.POST.get("admin_id")
        admin_user = get_object_or_404(CustomUser, id=admin_id)

        if 'add_admin' in request.POST:
            shop.admins.add(admin_user)  # ✅ เพิ่มแอดมินให้ร้านค้า
            admin_user.is_shop_admin = True  # ✅ กำหนดให้เป็นแอดมินร้าน
            admin_user.user_type = "shop_admin"  # ✅ เปลี่ยนประเภทผู้ใช้เป็นแอดมินร้าน
            admin_user.save()
            messages.success(request, f"เพิ่มแอดมิน {admin_user.username} แล้ว")

        elif 'remove_admin' in request.POST:
            shop.admins.remove(admin_user)  # ✅ ลบแอดมินออกจากร้าน
            if not admin_user.admin_shops.exists():  # ถ้าไม่ได้เป็นแอดมินร้านไหนแล้ว
                admin_user.is_shop_admin = False
                admin_user.user_type = "customer"  # ✅ เปลี่ยนประเภทผู้ใช้กลับเป็นลูกค้า
                admin_user.save()
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

    # ✅ ตรวจสอบสิทธิ์เฉพาะเจ้าของร้านหรือ Admin เท่านั้น
    if request.user != shop.owner and request.user not in shop.admins.all():
        return redirect('home')

    products = shop.products.all()
    product_forms = {product.id: ProductForm(instance=product) for product in products}

    if request.method == 'POST':
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')

        # ✅ เพิ่มสินค้า + เพิ่ม Stock
        if action == 'add_product':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                new_product = form.save(commit=False)
                new_product.shop = shop
                new_product.save()

                # ✅ สร้าง Stock สำหรับสินค้านี้
                Stock.objects.create(
                    shop=shop,
                    product=new_product,
                    quantity=request.POST.get('stock_quantity', 0),  # ค่าเริ่มต้นเป็น 0 ถ้าไม่ได้ใส่
                    price=new_product.price
                )

                messages.success(request, f"เพิ่มสินค้า {new_product.product_name} สำเร็จ!")
            return redirect('manage_products', shop_id=shop.id)

        # ✅ แก้ไขสินค้า + อัปเดต Stock
        elif action == 'edit_product' and product_id:
            product = get_object_or_404(Product, id=product_id, shop=shop)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                updated_product = form.save()

                # ✅ อัปเดตข้อมูล Stock
                stock = Stock.objects.filter(product=updated_product, shop=shop).first()
                if stock:
                    stock.quantity = request.POST.get('stock_quantity', stock.quantity)
                    stock.price = updated_product.price
                    stock.save()

                messages.success(request, f"แก้ไขสินค้า {updated_product.product_name} สำเร็จ!")
            return redirect('manage_products', shop_id=shop.id)

        # ✅ ลบสินค้า + ลบ Stock
        elif action == 'delete_product':
            product = Product.objects.filter(id=product_id, shop=shop).first()

            if product:
                # ✅ ลบ Stock ที่เกี่ยวข้องก่อน
                Stock.objects.filter(product=product, shop=shop).delete()

                product.delete()
                messages.success(request, f"ลบสินค้า {product.product_name} สำเร็จ!")
            else:
                messages.error(request, "ไม่พบสินค้าที่ต้องการลบ")

            return redirect('manage_products', shop_id=shop.id)

    return render(request, 'manage_products.html', {
        'shop': shop,
        'products': products,
        'product_forms': product_forms,
        'form': ProductForm(),
    })