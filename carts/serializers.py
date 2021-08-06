from django.db.models import fields
from carts.models import ProductInCart
from posts.models import Post
from rest_framework import serializers


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInCart
        exclude = ['created_at', 'created_by']
    
class AddToCartSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ProductInCart
        fields = ['product', 'number']