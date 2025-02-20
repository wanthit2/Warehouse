from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'shop', 'store', 'product_name', 'product_code', 'description', 'price', 'quantity', 'image',
                  'stock_quantity', 'added_date', 'category', 'unit', 'status']
