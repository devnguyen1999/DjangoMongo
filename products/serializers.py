from posts.models import Post
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    class Meta:
        model = Post
        exclude = ['created_at', 'created_by']
    

