from users.models import User
from djongo import models

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    short_content = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # image = models.ImageField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Posts'
