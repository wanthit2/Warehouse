from django import forms
from .models import Order
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import Product
from .models import Profile
from .models import UserProfile
from .models import Stock
from .models import CustomUser
from .models import ShopOwnerRequest
from .models import Shop
from .models import Store


STATUS_CHOICES = [
    ('pending', 'รอจัดส่ง'),
    ('shipped', 'จัดส่งแล้ว'),
    ('cancelled', 'ยกเลิก'),
]

SALES_CHANNEL_CHOICES = [
    ('หน้าร้าน', 'หน้าร้าน'),
    ('ออนไลน์', 'ออนไลน์'),
]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

        if self.product:
            self.fields['product_name'].initial = self.product.product_name
            self.fields['price'].initial = self.product.price

    def save(self, commit=True):
        order = super().save(commit=False)

        if self.product:
            # ดึงข้อมูลจาก product
            order.product_name = self.product.product_name
            order.price = self.product.price
            order.total_price = order.price * order.quantity

            # บันทึกค่า shop และ store
            order.shop_id = self.product.shop.id if self.product.shop else None
            order.store_id = self.product.store.id if self.product.store else None

            # กำหนดร้านค้า (shop) และ store
            order.shop = self.product.shop
            order.store = self.product.store

        if commit:
            order.save()
        return order


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'อีเมลของคุณ'}))

    class Meta:
        model = CustomUser  # ระบุว่าใช้ CustomUser แทน User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("รหัสผ่านไม่ตรงกัน")
        return cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['shop', 'store', 'product_name', 'product_code', 'description', 'price', 'quantity', 'image', 'stock_quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
        return product


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser  # ใช้ CustomUser แทน User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'profile_picture']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product_name', 'quantity', 'price', 'description']


class SearchStockForm(forms.Form):
    query = forms.CharField(label='ค้นหาสินค้า', max_length=100, required=False)

class ShopOwnerRequestForm(forms.ModelForm):
    class Meta:
        model = ShopOwnerRequest
        fields = ['store_name', 'description', 'email']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }
    # คุณสามารถเพิ่มการตรวจสอบข้อมูลในฟอร์มได้ที่นี่ถ้าจำเป็น
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if ShopOwnerRequest.objects.filter(email=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้ในการสมัครแล้ว")
        return email


class CustomUserProfileForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email']  # หรือฟิลด์ที่คุณต้องการให้กรอก

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("รหัสผ่านไม่ตรงกัน")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("กรุณากรอกชื่อผู้ใช้")

        # ตรวจสอบว่า username ซ้ำหรือไม่
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("ชื่อผู้ใช้นี้มีผู้ใช้งานแล้ว")

        return username


class AddAdminForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(is_shop_owner_approved=True), label='เลือกผู้ใช้งานที่ต้องการเพิ่มเป็นแอดมิน')

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'location', 'owner', 'admins']


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description', 'owner']