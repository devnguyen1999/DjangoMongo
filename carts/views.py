from products.models import Product
from carts.serializers import AddToCartSerializer, CartSerializer
from carts.models import ProductInCart
from carts.pagination import CustomPagination
from admins.decorators import admin_only
from rest_framework.decorators import parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import exceptions, status
from users.models import User
from rest_framework.views import APIView

# Create your views here.


class CartView(APIView):

    pagination_class = CustomPagination
    @permission_classes([IsAuthenticated])
    def get(self, request, format=None):
        products = ProductInCart.objects.filter(created_by=request.user.id)       
        products_serializer = CartSerializer(products, many=True)
        return JsonResponse(products_serializer.data, safe=False)

    @permission_classes([IsAuthenticated])
    def post(self, request, format=None):
        product_serializer = AddToCartSerializer(data=request.data)
        if product_serializer.is_valid():
            try:
                user = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                raise exceptions.NotFound('User not found.')
            product_serializer.validated_data['created_by'] = user
            product = product_serializer.validated_data['product']
            product_serializer.validated_data['name'] = product.name
            product_serializer.validated_data['price'] = product.price
            product_serializer.validated_data['image'] = product.images[0]
            product_serializer.save()
            return JsonResponse({'success': True}, status=status.HTTP_201_CREATED)
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    def delete(self, request, format=None):
        products = ProductInCart.objects.filter(created_by=request.user.id)       
        products.delete()
        return JsonResponse({'message': 'Cart has been emptied.'}, status=status.HTTP_204_NO_CONTENT)

class ProductInCartView(APIView):

    def get_object(self, pk):
        try:
            return ProductInCart.objects.get(pk=pk)
        except ProductInCart.DoesNotExist:
            raise exceptions.NotFound('Product not found.')

    @permission_classes([IsAuthenticated])
    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        product_serializer = AddToCartSerializer(product, data=request.data, partial=True)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse({'success': True})
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return JsonResponse({'message': 'The product has been removed from the cart.'}, status=status.HTTP_204_NO_CONTENT)

