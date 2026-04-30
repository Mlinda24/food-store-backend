from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_item_count', 'get_total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Item Count'
    
    def get_total_price(self, obj):
        total = sum(item.menu_item.price * item.quantity for item in obj.items.all())
        return f'MK{total:.2f}'
    get_total_price.short_description = 'Total Price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'menu_item', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'menu_item__name']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Changed from 'user' to 'customer' to match the model field
    list_display = ['id', 'customer', 'restaurant', 'status', 'total_price', 'created']
    list_filter = ['status', 'created']
    search_fields = ['customer__username', 'restaurant__name', 'delivery_address']
    readonly_fields = ['total_price', 'created', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'restaurant', 'status', 'total_price')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'note')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'menu_item', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['order__customer__username', 'menu_item__name']