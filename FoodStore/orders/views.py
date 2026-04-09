from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from restaurants.models import MenuItem

# ----------------- Cart -----------------
class CartViewSet(viewsets.ViewSet):
    """
    Handles user cart:
    - list items
    - add item
    - update quantity
    - remove item
    """

    def get_cart(self, request):
        cart, created = Cart.objects.get_or_create(customer=request.user)
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart(request)
        menu_item_id = request.data.get('menu_item')
        quantity = int(request.data.get('quantity', 1))
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)

        # Update restaurant reference if empty
        if not cart.restaurant:
            cart.restaurant = menu_item.restaurant
            cart.save()

        # Ensure same restaurant
        if cart.restaurant != menu_item.restaurant:
            return Response({"detail": "All items must be from the same restaurant."},
                            status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


# ----------------- Order -----------------
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created')

    def perform_create(self, serializer):
        """
        Create an order from the current user's cart.
        """
        cart = get_object_or_404(Cart, customer=self.request.user)
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")

        total_price = 0
        order = serializer.save(customer=self.request.user, restaurant=cart.restaurant)
        
        for item in cart.items.all():
            price = item.menu_item.price
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                price=price * item.quantity
            )
            total_price += price * item.quantity

        order.total_price = total_price
        order.save()
        cart.items.all().delete()  # clear cart after order