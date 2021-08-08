from orders.MoMo import payment_by_MoMo
from orders.VNPay import payment_by_VNPay
from orders.serializers import CreateOrderSerializer, OrderSerializer
from orders.models import Order, ProductInOrder
from carts.pagination import CustomPagination
from admins.decorators import admin_only
from rest_framework.decorators import parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http.response import HttpResponseRedirect, JsonResponse
from rest_framework import exceptions, status
from users.models import User
from rest_framework.views import APIView

# Create your views here.


class OrdersView(APIView):

    pagination_class = CustomPagination

    @permission_classes([IsAuthenticated])
    def get(self, request, format=None):
        orders = Order.objects.filter(created_by=request.user.id)
        orders_serializer = OrderSerializer(orders, many=True)
        return JsonResponse(orders_serializer.data, safe=False)

    @permission_classes([IsAuthenticated])
    def post(self, request, format=None):
        order_serializer = CreateOrderSerializer(data=request.data)
        if order_serializer.is_valid():
            try:
                user = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                raise exceptions.NotFound('User not found.')
            order_serializer.validated_data['created_by'] = user
            order_serializer.validated_data['total_price'] = order_serializer.validated_data[
                'price_of_products'] + order_serializer.validated_data['shipping_fee']
            order = order_serializer.save()
            if order.payment_method is 'COD':
                pass
            elif order.payment_method is 'VNP':
                data = {
                    'order_type': 'billpayment',
                    'order_id': order.id,
                    'amount': order.total_price,
                    'order_desc': 'Thanh toan don hang',
                    'bank_code': None,
                    'language': None
                }
                url_payment = payment_by_VNPay(data)
                print(url_payment)
                return HttpResponseRedirect(redirect_to=url_payment)
            elif order.payment_method is 'MOM':
                data = {
                    'orderInfo': 'Thanh toan don hang',
                    'amount': order.total_price,
                    'orderId': order.id,
                }
                url_payment = payment_by_MoMo(data)
                print(url_payment)
                return HttpResponseRedirect(redirect_to=url_payment)
            else:
                pass
        return JsonResponse(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    def delete(self, request, format=None):
        orders = Order.objects.filter(created_by=request.user.id)
        orders.delete()
        return JsonResponse({'message': 'All orders have been cleared.'}, status=status.HTTP_204_NO_CONTENT)


class VNPayPaymentReturnView(APIView):
    def get(self, request, format=None):
        if request.query_params['vnp_ResponseCode'] == '00':
            try:
                order = Order.objects.get(
                    pk=request.query_params['vnp_TxnRef'])
            except User.DoesNotExist:
                raise exceptions.NotFound('Order not found.')
            order.is_paid = True
            order.save()
        return JsonResponse({'response_code': request.query_params['vnp_ResponseCode']})


class MoMoPaymentReturnView(APIView):
    def get(self, request, format=None):
        if request.query_params['errorCode'] == '0':
            try:
                order = Order.objects.get(
                    pk=request.query_params['orderId'])
            except User.DoesNotExist:
                raise exceptions.NotFound('Order not found.')
            order.is_paid = True
            order.save()
        return JsonResponse({'errorCode': request.query_params['errorCode'], 'message': request.query_params['message']})


class OrderView(APIView):

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise exceptions.NotFound('Order not found.')

    @permission_classes([IsAuthenticated])
    def patch(self, request, pk, format=None):
        pass

    @permission_classes([IsAuthenticated])
    def delete(self, request, pk, format=None):
        order = self.get_object(pk)
        order.delete()
        return JsonResponse({'message': 'Order has been deleted.'}, status=status.HTTP_204_NO_CONTENT)
