from categories.models import Category
from users.models import User
from djongo import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)
    fake_price = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    images = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Products'

class ProductComment(models.Model):
    comment = models.TextField()
    images = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.comment

    class Meta:
        db_table = 'Product_comments'
