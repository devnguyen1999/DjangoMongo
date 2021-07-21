from django.db.models.fields import CharField
from rest_framework import serializers
from posts.models import Post, Image


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'short_content', 'content']


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ('image', 'uploaded_at')


class DeleteImageSerializer(serializers.Serializer):
    image =serializers.CharField(required=True)