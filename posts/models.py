from users.models import User
from djongo import models
import os
from django.conf import settings
from django.utils import timezone

# Create your models here.


def post_upload_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"posts/{instance.pk}/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"


class Post(models.Model):
    title = models.CharField(max_length=100)
    short_content = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(
        upload_to=post_upload_to, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by= models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Posts'


def image_upload_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"posts/images_in_posts/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"


class Image(models.Model):
    image = models.ImageField(
        upload_to=image_upload_to, blank=False, null=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
