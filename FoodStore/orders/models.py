from django.db import models
from django.conf import settings
from restaurants.models import MenuItem, Restaurant

class Cart(models.Model):
    customer   = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)
    updated    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.customer}"

class CartItem(models.Model):
    cart      = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class Order(models.Model):
    PENDING   = 'pending'
    CONFIRMED = 'confirmed'
    PREPARING = 'preparing'
    READY     = 'ready'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING,   'Pending'),
        (CONFIRMED, 'Confirmed'),
        (PREPARING, 'Preparing'),
        (READY,     'Ready for Pickup'),
        (CANCELLED, 'Cancelled'),
    ]
    customer    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant  = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note        = models.TextField(blank=True)
    created     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

class OrderItem(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField()
    price     = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot price

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"