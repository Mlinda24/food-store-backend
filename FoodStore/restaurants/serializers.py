from rest_framework import serializers
from .models import Restaurant, Category, MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MenuItem
        fields = '__all__'
        read_only_fields = ['restaurant']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = '__all__'
        read_only_fields = ['restaurant']

class RestaurantSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model  = Restaurant
        fields = '__all__'
        read_only_fields = ['owner']