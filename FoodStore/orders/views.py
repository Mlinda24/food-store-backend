from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from restaurants.models import MenuItem
from rest_framework import serializers as rest_serializers

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_or_create_cart(self, user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        """Get current user's cart"""
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_or_create_cart(request.user)
        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity', 1)

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id, is_available=True)
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = self.get_or_create_cart(request.user)
        menu_item_id = request.data.get('menu_item_id')

        try:
            cart_item = CartItem.objects.get(cart=cart, menu_item_id=menu_item_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update item quantity"""
        cart = self.get_or_create_cart(request.user)
        menu_item_id = request.data.get('menu_item_id')
        quantity = request.data.get('quantity', 0)

        try:
            cart_item = CartItem.objects.get(cart=cart, menu_item_id=menu_item_id)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
        except CartItem.DoesNotExist:
            pass

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_or_create_cart(request.user)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        
        # Get or create cart for the user
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Check if cart has items
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            raise rest_serializers.ValidationError({"detail": "Cart is empty. Add items to cart before placing an order."})
        
        with transaction.atomic():
            # Calculate total price
            total_price = sum(item.menu_item.price * item.quantity for item in cart_items)
            
            # Create the order
            order = serializer.save(
                user=user,
                restaurant=cart_items.first().menu_item.restaurant,
                total_price=total_price,
                status='pending'
            )
            
            # Create order items from cart items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    price=cart_item.menu_item.price
                )
            
            # Clear the cart
            cart_items.delete()
        
        return order