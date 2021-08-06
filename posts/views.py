from posts.pagination import CustomPagination
from categories.models import Category
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
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
import cloudinary.uploader
from django.core.serializers import serialize 
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

class PostsView(APIView):
    pagination_class = CustomPagination
    def get(self, request, format=None):
        post = Post.objects.all()        
        post_serializer = PostSerializer(post, many=True)
        return JsonResponse(post_serializer.data, safe=False)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    @parser_classes([MultiPartParser, FormParser])
    def post(self, request, format=None):
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            try:
                user = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                raise exceptions.NotFound('Admin not found.')
            post_serializer.validated_data['created_by'] = user
            try:
                category = Category.objects.get(pk=post_serializer.validated_data['category'])
            except Category.DoesNotExist:
                raise exceptions.NotFound('Category not found.')
            post_serializer.validated_data['category'] = category
            upload_data = cloudinary.uploader.upload(
                post_serializer.validated_data['image'], folder='djangomongo/posts')
            post_serializer.validated_data['image'] = upload_data['secure_url']
            post_serializer.save()
            return JsonResponse({'success': True}, status=status.HTTP_201_CREATED, safe=False)
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
            return JsonResponse({'success': True}, status=status.HTTP_200_OK)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return JsonResponse({'message': 'Post was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ImageView(APIView):

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    @parser_classes([MultiPartParser, FormParser])
    def post(self, request, format=None):
        image_serializer = UploadImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image = image_serializer.validated_data['image']
            upload_data = cloudinary.uploader.upload(
                image, folder='djangomongo/posts')
            return JsonResponse(upload_data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, format=None):
        image_serializer = DeleteImageSerializer(data=request.data)
        if image_serializer.is_valid():
            public_id = image_serializer.validated_data['public_id']
            result = cloudinary.uploader.destroy(public_id)
            return JsonResponse({'success': True}, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse(image_serializer.errors,  status=status.HTTP_400_BAD_REQUEST)

