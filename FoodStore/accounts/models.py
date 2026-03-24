# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    CUSTOMER    = 'customer'
    RESTAURANT  = 'restaurant'
    ROLE_CHOICES = [
        (CUSTOMER,   'Customer'),
        (RESTAURANT, 'Restaurant Owner'),
    ]
    role  = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)