from products.models import Product
from users.models import User
from djongo import models

# Create your models here.

class ProductInCart(models.Model):
    product = models.ManyToManyField(Product)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    image = models.URLField(max_length=200)
    number = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Products_in_carts'