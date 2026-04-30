from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, MenuItem

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cart'
    )
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    customization = models.JSONField(default=dict, blank=True)
    special_instructions = models.TextField(blank=True, default='')
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        base = f"{self.quantity} x {self.menu_item.name}"
        if self.customization:
            cust_str = ', '.join([f"{k}: {v}" for k, v in self.customization.items()])
            return f"{base} ({cust_str})"
        return base

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'menu_item', 'customization']


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.TextField(blank=True, default='')
    note = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customization = models.JSONField(default=dict, blank=True)
    special_instructions = models.TextField(blank=True, default='')

    @property
    def total(self):
        return self.price * self.quantity

    @property
    def display_name(self):
        base = self.menu_item.name
        if self.customization:
            if 'relish' in self.customization:
                return f"{base} with {self.customization['relish']}"
            cust_str = ', '.join([f"{k}: {v}" for k, v in self.customization.items()])
            return f"{base} ({cust_str})"
        return base

    def __str__(self):
        base = f"{self.quantity} x {self.menu_item.name}"
        if self.customization:
            cust_str = ', '.join([f"{k}: {v}" for k, v in self.customization.items()])
            return f"{base} ({cust_str})"
        return base

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'