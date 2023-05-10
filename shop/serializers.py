from decimal import Decimal

from rest_framework import serializers
from .models import Category, Product, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', )


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'description', 'price', 'category', ]


class CartSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products', 'count', ]
        read_only_fields = ['id', 'user']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'phone_number', 'delivery_address', ]
        read_only_fields = ['id', 'user', 'total_price', ]
