from carts.views import CartView, ProductInCartView
from django.urls import path

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('product/<int:pk>', ProductInCartView.as_view(), name='product_in_cart'),
]