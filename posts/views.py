from django.conf import settings
import os
from admins.decorators import admin_only
from rest_framework.decorators import parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from posts.serializers import DeleteImageSerializer, UploadImageSerializer, PostSerializer
from django.http.response import JsonResponse
from rest_framework import exceptions, status
from posts.models import Post
from users.models import User
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.


class CreatePostView(APIView):

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def post(self, request, format=None):
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            try:
                author =  User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                raise exceptions.NotFound('User not found.')
            post_serializer.validated_data['created_by'] = author.id
            post_serializer.save()
            return JsonResponse(post_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostView(APIView):

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise exceptions.NotFound('Post not found.')

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        post_serializer = PostSerializer(post)
        return JsonResponse(post_serializer.data)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def patch(self, request, pk, format=None):
        post = self.get_object(pk)
        post_serializer = PostSerializer(post, data=request.data, partial=True)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse(post_serializer.data)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return JsonResponse({'message': 'Post was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ImageView(APIView):

    @parser_classes([MultiPartParser, FormParser])
    def post(self, request, format=None):
        image_serializer = UploadImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image_serializer.save()
            return JsonResponse(image_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        image_serializer = DeleteImageSerializer(data=request.data)
        if image_serializer.is_valid():
            try:
                os.remove(os.path.join(
                    settings.BASE_DIR, image_serializer.validated_data["image"]))
            except OSError:
                JsonResponse({'message': 'Image can not be deleted.'},
                             status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(image_serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse(image_serializer.errors,  status=status.HTTP_400_BAD_REQUEST)
