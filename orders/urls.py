
from orders.views import MoMoPaymentReturnView, OrderView, OrdersView, VNPayPaymentReturnView
from django.urls import path

urlpatterns = [
    path('', OrdersView.as_view(), name='orders'),
    path('vnpay_payment_return', VNPayPaymentReturnView.as_view(), name='vnpay_payment_return'),
    path('momo_payment_return', MoMoPaymentReturnView.as_view(), name='momo_payment_return'),
    path('detail/<int:pk>', OrderView.as_view(), name='order_detail'),
]