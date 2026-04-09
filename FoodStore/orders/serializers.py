from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem

# ----------------- Cart -----------------
class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model  = CartItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Cart
        fields = ['id', 'customer', 'restaurant', 'items', 'updated']

# ----------------- Order -----------------
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model  = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = ['id', 'restaurant', 'status', 'total_price', 'note', 'items', 'created']
        read_only_fields = ['customer', 'status', 'total_price']