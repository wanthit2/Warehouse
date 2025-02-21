from django import forms
from .models import Order, Product, UserProfile, Stock, CustomUser, ShopOwnerRequest, Shop, Category
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


STATUS_CHOICES = [
    ('pending', 'รอจัดส่ง'),
    ('shipped', 'จัดส่งแล้ว'),
    ('cancelled', 'ยกเลิก'),
]

SALES_CHANNEL_CHOICES = [
    ('หน้าร้าน', 'หน้าร้าน'),
    ('ออนไลน์', 'ออนไลน์'),
]


### 🔹 แก้ไข `OrderForm` (ลบ `store`)
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
            order.product_name = self.product.product_name
            order.price = self.product.price
            order.total_price = order.price * order.quantity

            # ✅ ใช้ shop แทน store
            order.shop_id = self.product.shop.id if self.product.shop else None
            order.shop = self.product.shop

        if commit:
            order.save()
        return order


### 🔹 แก้ไข `ProductForm` (ลบ `store`)
class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="เลือกหมวดหมู่",  # ✅ เปลี่ยนข้อความ dropdown
        required=True,
        label="หมวดหมู่"  # ✅ เปลี่ยน Label เป็นภาษาไทย
    )
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'price', 'quantity','category', 'unit', 'image', 'stock_quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        self.shop = kwargs.pop('shop', None)  # ✅ รับ shop จาก views
        super().__init__(*args, **kwargs)

        # ✅ ให้สามารถเลือกหมวดหมู่ได้
        self.fields['category'].queryset = Category.objects.all()


    def save(self, commit=True):
        product = super().save(commit=False)
        if self.shop:
            product.shop = self.shop  # ✅ กำหนดร้านอัตโนมัติ
        if commit:
            product.save()
        return product



### 🔹 ฟอร์มสมัครสมาชิก
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





### 🔹 ฟอร์มแก้ไขโปรไฟล์
class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="ชื่อผู้ใช้")
    email = forms.EmailField(required=True, label="อีเมล")

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'address']
        labels = {
            'profile_picture': "รูปโปรไฟล์",
            'address': "ที่อยู่",
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'กรอกที่อยู่ของคุณ...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        if commit:
            profile.save()
        return profile


### 🔹 ฟอร์มคลังสินค้า
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['shop', 'product', 'quantity', 'price', 'description']


class SearchStockForm(forms.Form):
    query = forms.CharField(label='ค้นหาสินค้า', max_length=100, required=False)



class ShopOwnerRequestForm(forms.ModelForm):
    class Meta:
        model = ShopOwnerRequest
        fields = ['shop_name', 'description', 'email']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if ShopOwnerRequest.objects.filter(email=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้ในการสมัครแล้ว")
        return email


### 🔹 ฟอร์มเพิ่มแอดมินร้านค้า
class AddAdminForm(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(is_shop_owner_approved=True), label='เลือกผู้ใช้งานที่ต้องการเพิ่มเป็นแอดมิน')


### 🔹 ฟอร์มร้านค้า
class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'location', 'owner', 'admins']



class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser  # ใช้ CustomUser แทน User
        fields = ['first_name', 'last_name', 'email']



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
