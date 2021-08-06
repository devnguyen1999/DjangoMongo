from djongo import models

# Create your models here.


class Category(models.Model):
    MODULE_CHOICES = [
        ('POS', 'Posts'),
        ('PRO', 'Products'),
    ]
    name = models.CharField(max_length=50)
    category_of = models.CharField(
        max_length=3,
        choices=MODULE_CHOICES,
    )
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Categories'
