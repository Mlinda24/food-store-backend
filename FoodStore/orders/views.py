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
        item_id  = request.data.get('menu_item')
        quantity = int(request.data.get('quantity', 1))
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item_id=item_id)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        cart.items.all().delete()
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
        cart     = Cart.objects.get(customer=self.request.user)
        items    = cart.items.select_related('menu_item')
        total    = sum(i.menu_item.price * i.quantity for i in items)
        order    = serializer.save(customer=self.request.user, total_price=total,
                                   restaurant=cart.restaurant)
        for i in items:
            OrderItem.objects.create(order=order, menu_item=i.menu_item,
                                     quantity=i.quantity, price=i.menu_item.price)
        cart.items.all().delete()

    @action(detail=True, methods=['patch'], permission_classes=[IsRestaurantOwner])
    def update_status(self, request, pk=None):
        order  = self.get_object()
        new_st = request.data.get('status')
        order.status = new_st
        order.save()
        return Response({'status': order.status})