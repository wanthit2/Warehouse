# ในไฟล์ inventory/decorators.py

from django.contrib.auth.decorators import user_passes_test

# สร้าง decorator ที่จะตรวจสอบว่า user เป็นแอดมิน (is_staff)
def admin_required(function):
    return user_passes_test(lambda user: user.is_staff)(function)
