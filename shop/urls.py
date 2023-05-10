from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from rest_framework import routers

from shop.views import CategoryApiView, ProductApiView, CartApiView, OrderApiView

router = routers.SimpleRouter()
router.register(r'categories', CategoryApiView, basename='categories')
router.register(r'products', ProductApiView, basename='products')
router.register(r'cart', CartApiView, basename='cart')
router.register(r'order', OrderApiView, basename='order')

urlpatterns = [
    path('', include(router.urls), )

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)