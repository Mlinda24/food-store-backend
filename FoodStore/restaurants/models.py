# Create your models here.
from django.db import models
from django.conf import settings

class Restaurant(models.Model):
    owner    = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name     = models.CharField(max_length=255)
    address  = models.TextField()
    phone    = models.CharField(max_length=20, blank=True)
    image    = models.ImageField(upload_to='restaurants/', blank=True)
    is_open  = models.BooleanField(default=True)
    created  = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name       = models.CharField(max_length=100)

class MenuItem(models.Model):
    restaurant  = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    image       = models.ImageField(upload_to='menu/', blank=True)
    is_available = models.BooleanField(default=True)