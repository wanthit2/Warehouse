from django import forms
from .models import Order
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product
from .models import Profile



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
        # รับ product ผ่าน kwargs
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # คำนวณยอดรวมก่อนบันทึก
        order = super().save(commit=False)
        if self.product:
            order.product_code = self.product.product_code
            order.name = self.product.product_name
            order.price = self.product.price
            order.total = order.price * order.quantity
        if commit:
            order.save()
        return order

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

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'profile_picture']