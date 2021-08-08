from products.models import Product
from users.models import User, UserAddress
from djongo import models

# Create your models here.


class Order(models.Model):
    PAYMENT_METHODS_CHOICES = [
        ('COD', 'Cash On Delivery'),
        ('VNP', 'VNPay'),
        ('MOM', 'Momo')
    ]
    price_of_products = models.PositiveIntegerField()
    shipping_fee = models.PositiveIntegerField()
    total_price = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # delivery_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.CharField(
        max_length=3,
        choices=PAYMENT_METHODS_CHOICES,
    )
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.total_price

    class Meta:
        db_table = 'Orders'


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    image = models.URLField(max_length=200)
    number = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Products_in_orders'
