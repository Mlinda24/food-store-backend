from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Restaurant, MenuItem, Category
from .serializers import (
    RestaurantSerializer, RestaurantListSerializer,
    MenuItemSerializer, MenuItemPublicSerializer,
    MenuItemWithRestaurantSerializer, CategorySerializer
)
from accounts.permissions import IsRestaurantOwner


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public landing page API.
    - Not logged in → menu items only (no restaurant info)
    - Logged in     → menu items with restaurant name
    """
    def get_queryset(self):
        return MenuItem.objects.filter(is_available=True).select_related('restaurant')

    def get_permissions(self):
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return MenuItemWithRestaurantSerializer   # includes restaurant name
        return MenuItemPublicSerializer               # no restaurant info


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    Authenticated users see restaurant list.
    Clicking a restaurant shows full details + full menu.
    """
    def get_queryset(self):
        return Restaurant.objects.filter(is_open=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantSerializer        # full details + full menu
        return RestaurantListSerializer        # lightweight list

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRestaurantOwner()]
        return [permissions.IsAuthenticated()]  # must be logged in to see restaurants

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RestaurantMenuViewSet(viewsets.ModelViewSet):
    """
    Restaurant owner manages their own menu items.
    """
    serializer_class   = MenuItemSerializer
    permission_classes = [IsRestaurantOwner]

    def get_queryset(self):
        return MenuItem.objects.filter(restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)