from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CategoryModel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,unique=True, null=True, blank=True)
    def __str__(self):
        return self.name

class BookModel(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='book_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(CategoryModel, related_name='books', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ReviewModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(BookModel, related_name='reviews', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)