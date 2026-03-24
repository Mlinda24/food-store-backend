from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'customer', 'restaurant', 'status', 'total_price', 'created']
    list_filter   = ['status']
    search_fields = ['customer__username', 'restaurant__name']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ['order', 'menu_item', 'quantity', 'price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ['customer', 'restaurant', 'updated']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display  = ['cart', 'menu_item', 'quantity']