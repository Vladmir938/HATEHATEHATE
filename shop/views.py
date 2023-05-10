from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import LoginForm
from .models import Category, Product, Cart, Order, OrderItem, CartItem
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, OrderSerializer
from .permissions import CategoryPermission


class CategoryApiView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]


class ProductApiView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [CategoryPermission]


class CartApiView(LoginRequiredMixin, viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        product_id = request.data.get('product_id')
        product = Product.objects.get(id=product_id)
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        product_id = request.data.get('product_id')
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        if cart is not None:
            cart.products.remove(product_id)
            cart.save()
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        cart.save()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class OrderApiView(LoginRequiredMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        order = Order.objects.create(user=user)
        cart = Cart.objects.get(user=user)
        cart_items = cart.cart_items.all()

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price * cart_item.quantity
            )

        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def perform_create(self, serializer):
        try:
            cart = Cart.objects.get(user=self.request.user)
        except Cart.MultipleObjectsReturned:
            cart = Cart.objects.filter(user=self.request.user).last()
        items = []
        total_price = 0
        for product in cart.products.all():
            item = OrderItem(product=product, quantity=cart.products.filter(id=product.id).count())
            item.save()
            items.append(item)
            total_price += item.price
        order = serializer.save(
            user=self.request.user,
            total_price=total_price,
            phone_number=self.request.data.get('phone_number'),
            delivery_address=self.request.data.get('delivery_address'),
        )
        for item in items:
            order.items.add(item)
        cart.delete()


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'