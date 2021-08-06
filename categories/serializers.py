from categories.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField()
    class Meta:
        model = Category
        fields = ['name', 'category_of', 'parent']
