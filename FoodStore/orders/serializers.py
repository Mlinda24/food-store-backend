from django.db import models
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from restaurants.serializers import MenuItemSerializer

class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'menu_item', 'menu_item_id', 'quantity', 
                  'customization', 'special_instructions', 'added_at']
        read_only_fields = ['id', 'cart', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'restaurant', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    def get_total_price(self, obj):
        return sum(item.menu_item.price * item.quantity for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_price = serializers.DecimalField(source='menu_item.price', read_only=True, max_digits=10, decimal_places=2)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'menu_item_name', 'menu_item_price', 
                  'quantity', 'price', 'customization', 'special_instructions', 'display_name']
        read_only_fields = ['id', 'order', 'menu_item_name', 'menu_item_price']
    
    def get_display_name(self, obj):
        return obj.display_name

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'customer_phone', 'restaurant', 'restaurant_name', 
                  'items', 'status', 'total_price', 'delivery_address', 'note', 'created', 'updated_at']
        read_only_fields = ['id', 'customer', 'status', 'total_price', 'created', 'updated_at']
    
    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.username
        return 'Customer'
    
    def get_customer_phone(self, obj):
        if obj.customer and obj.customer.phone:
            return obj.customer.phone
        return 'No phone'