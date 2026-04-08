# orders/views.py - CORRECTED VERSION
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from accounts.permissions import IsCustomer, IsRestaurantOwner

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsCustomer]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        item_id = request.data.get('menu_item')
        quantity = int(request.data.get('quantity', 1))
        
        # Check if cart has restaurant
        menu_item = MenuItem.objects.get(id=item_id)
        if cart.restaurant and cart.restaurant != menu_item.restaurant:
            return Response(
                {'error': 'Cart already has items from a different restaurant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set restaurant if not set
        if not cart.restaurant:
            cart.restaurant = menu_item.restaurant
            cart.save()
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            menu_item_id=item_id
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        cart = Cart.objects.get(customer=request.user)
        item_id = request.data.get('cart_item_id')
        cart.items.filter(id=item_id).delete()
        
        # If cart becomes empty, clear restaurant
        if not cart.items.exists():
            cart.restaurant = None
            cart.save()
        
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        cart = Cart.objects.get(customer=request.user)
        item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        
        if quantity <= 0:
            cart.items.filter(id=item_id).delete()
        else:
            cart_item = cart.items.get(id=item_id)
            cart_item.quantity = quantity
            cart_item.save()
        
        # If cart becomes empty, clear restaurant
        if not cart.items.exists():
            cart.restaurant = None
            cart.save()
        
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        cart.items.all().delete()
        cart.restaurant = None
        cart.save()
        return Response({'detail': 'Cart cleared.'})

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Order.objects.filter(customer=user)
        if user.role == 'restaurant':
            return Order.objects.filter(restaurant__owner=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        # Convert cart → order
        cart = Cart.objects.get(customer=self.request.user)
        
        if not cart.restaurant:
            raise serializers.ValidationError('Cart is empty')
        
        items = cart.items.select_related('menu_item')
        total = sum(i.menu_item.price * i.quantity for i in items)
        
        order = serializer.save(
            customer=self.request.user,
            total_price=total,
            restaurant=cart.restaurant
        )
        
        for i in items:
            OrderItem.objects.create(
                order=order,
                menu_item=i.menu_item,
                quantity=i.quantity,
                price=i.menu_item.price
            )
        
        # Clear cart after order
        cart.items.all().delete()
        cart.restaurant = None
        cart.save()

    @action(detail=True, methods=['patch'], permission_classes=[IsRestaurantOwner])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'cancelled']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        return Response({'status': order.status})