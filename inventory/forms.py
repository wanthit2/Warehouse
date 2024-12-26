from django import forms
from .models import Order
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product


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
        fields = ['order_id', 'order_date', 'customer', 'sales_channel', 'destination', 'items', 'status']
        labels = {
            'order_id': 'รหัสคำสั่ง',
            'order_date': 'วันที่',
            'customer': 'ลูกค้า',
            'sales_channel': 'ช่องทางการขาย',
            'destination': 'ปลายทาง',
            'items': 'จำนวนสินค้า',  # เปลี่ยนเป็น "จำนวนสินค้า"
            'status': 'สถานะ',
        }
        widgets = {
            'order_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'รหัสคำสั่ง'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'customer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อลูกค้า'}),
            'sales_channel': forms.Select(choices=SALES_CHANNEL_CHOICES, attrs={'class': 'form-select'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ปลายทาง'}),
            'items': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'จำนวนสินค้า'}),
            'status': forms.Select(choices=STATUS_CHOICES, attrs={'class': 'form-select'}),
        }



class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'อีเมลของคุณ'}))
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={'placeholder': 'ยืนยันรหัสผ่าน'})
    )

    class Meta:
        model = User
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

#class ProductForm(forms.ModelForm):
#    class Meta:
 #       model = Product
  #      fields = ['product_name', 'product_code', 'description', 'price', 'quantity']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'product_name', 'description', 'quantity', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }