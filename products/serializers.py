from products.models import Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ImageField(required=True)
    class Meta:
        model = Product
        exclude = ['created_at', 'created_by']
    

