from posts.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    class Meta:
        model = Post
        exclude = ['created_at', 'created_by']



class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)


class DeleteImageSerializer(serializers.Serializer):
    public_id = serializers.CharField(required=True)
