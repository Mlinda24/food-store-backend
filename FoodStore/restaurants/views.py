# Create your views here.
from rest_framework import viewsets, permissions
from .models import Restaurant, MenuItem, Category
from .serializers import RestaurantSerializer, MenuItemSerializer, CategorySerializer
from accounts.permissions import IsRestaurantOwner

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.filter(is_open=True)
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRestaurantOwner()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        return MenuItem.objects.filter(restaurant__owner=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsRestaurantOwner()]

    def perform_create(self, serializer):
        restaurant = self.request.user.restaurant
        serializer.save(restaurant=restaurant)