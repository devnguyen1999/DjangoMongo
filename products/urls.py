from django.urls import path
from products.views import ProductView, ProductsView

urlpatterns = [
    path('', ProductsView.as_view(), name='products'),
    path('detail/<int:pk>', ProductView.as_view(), name='product_detail'),
]