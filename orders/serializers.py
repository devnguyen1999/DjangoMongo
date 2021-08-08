from django.db.models import fields
from orders.models import Order, ProductInOrder
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
    
class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['price_of_products', 'shipping_fee', 'payment_method']