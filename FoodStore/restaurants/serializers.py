from rest_framework import serializers
from .models import Restaurant, Category, MenuItem


class MenuItemPublicSerializer(serializers.ModelSerializer):
    """Used for unauthenticated users — no restaurant info"""
    class Meta:
        model  = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available']


class MenuItemWithRestaurantSerializer(serializers.ModelSerializer):
    """Used for logged in users — includes restaurant name"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model  = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image',
                  'is_available', 'restaurant', 'restaurant_name']


class MenuItemSerializer(serializers.ModelSerializer):
    """Used by restaurant owner to manage their menu"""
    class Meta:
        model        = MenuItem
        fields       = '__all__'
        read_only_fields = ['restaurant']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = '__all__'
        read_only_fields = ['restaurant']


class RestaurantSerializer(serializers.ModelSerializer):
    """Full restaurant details with complete menu — shown after clicking a restaurant"""
    menu_items = MenuItemSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model  = Restaurant
        fields = '__all__'
        read_only_fields = ['owner']


class RestaurantListSerializer(serializers.ModelSerializer):
    """Lightweight — just restaurant info for the list view"""
    class Meta:
        model  = Restaurant
        fields = ['id', 'name', 'address', 'phone', 'image', 'is_open']