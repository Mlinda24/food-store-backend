from rest_framework import serializers
from .models import Restaurant, Category, MenuItem

# ------------------------------
# MenuItem Serializers
# ------------------------------
class MenuItemPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available']

class MenuItemWithRestaurantSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available', 'restaurant', 'restaurant_name']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['restaurant']

# ------------------------------
# Category Serializer
# ------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['restaurant']

# ------------------------------
# Restaurant Serializer
# ------------------------------
class RestaurantSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['owner']

class RestaurantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone', 'image', 'is_open']