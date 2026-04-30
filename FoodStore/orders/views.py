from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
from restaurants.models import MenuItem, Restaurant

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart(request)
        menu_item_id = request.data.get('menu_item_id')
        quantity = int(request.data.get('quantity', 1))
        customization = request.data.get('customization', {})
        special_instructions = request.data.get('special_instructions', '')

        if not menu_item_id:
            return Response(
                {'error': 'menu_item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        menu_item = get_object_or_404(MenuItem, id=menu_item_id)

        if not cart.restaurant:
            cart.restaurant = menu_item.restaurant
            cart.save()

        if cart.restaurant and cart.restaurant.id != menu_item.restaurant.id:
            return Response(
                {'error': 'Cannot add items from different restaurants'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            customization=customization,
            defaults={
                'quantity': quantity,
                'special_instructions': special_instructions
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        cart = self.get_cart(request)
        cart_item_id = request.data.get('cart_item_id')
        quantity = int(request.data.get('quantity', 1))

        if not cart_item_id:
            return Response(
                {'error': 'cart_item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

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
        cart_item_id = request.data.get('cart_item_id')

        if not cart_item_id:
            return Response(
                {'error': 'cart_item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        cart_item.delete()

        if not cart.items.exists():
            cart.restaurant = None
            cart.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        cart.restaurant = None
        cart.save()
        
        return Response(
            {'message': 'Cart cleared successfully'},
            status=status.HTTP_200_OK
        )


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(f"📋 OrderViewSet.get_queryset - User: {user.username}, Role: {user.role}")
        
        if user.role == 'restaurant':
            try:
                restaurant = Restaurant.objects.get(owner=user)
                print(f"   Restaurant found: {restaurant.name} (ID: {restaurant.id})")
                queryset = Order.objects.filter(restaurant=restaurant).order_by('-created')
                print(f"   Orders found: {queryset.count()}")
                return queryset
            except Restaurant.DoesNotExist:
                print("   No restaurant found for this user")
                return Order.objects.none()
        
        # For customers, show their own orders
        queryset = Order.objects.filter(customer=user).order_by('-created')
        print(f"   Customer orders found: {queryset.count()}")
        return queryset

    def list(self, request, *args, **kwargs):
        print("📋 OrderViewSet.list called")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(f"   Returning {len(serializer.data)} orders")
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests to update order status"""
        print(f"📝 PATCH request received for order")
        instance = self.get_object()
        new_status = request.data.get('status')
        
        if new_status:
            print(f"   Updating status to: {new_status}")
            valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
            if new_status in valid_statuses:
                instance.status = new_status
                instance.save()
                print(f"✅ Order #{instance.id} status updated to: {instance.status}")
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("📝 Creating new order...")
        print(f"   User: {request.user.username}")
        
        try:
            cart = Cart.objects.get(user=request.user)
            print(f"   Cart found: ID {cart.id}")
            print(f"   Cart items: {cart.items.count()}")
            print(f"   Cart restaurant: {cart.restaurant}")
        except Cart.DoesNotExist:
            print("   Cart not found")
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            print("   Cart is empty")
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.restaurant:
            print("   No restaurant selected")
            return Response(
                {'error': 'No restaurant selected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total price
        total_price = sum(item.menu_item.price * item.quantity for item in cart.items.all())
        print(f"   Total price: {total_price}")

        # Get delivery address from request
        delivery_address = request.data.get('delivery_address', '')
        if not delivery_address:
            print("   No delivery address provided")
            return Response(
                {'error': 'Delivery address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        print(f"   Delivery address: {delivery_address}")

        # Create order
        order = Order.objects.create(
            customer=request.user,
            restaurant=cart.restaurant,
            total_price=total_price,
            delivery_address=delivery_address,
            note=request.data.get('note', ''),
            status='pending'
        )
        print(f"   Order created: #{order.id}")

        # Create order items from cart items
        item_count = 0
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price=cart_item.menu_item.price,
                customization=cart_item.customization,
                special_instructions=cart_item.special_instructions
            )
            item_count += 1
            print(f"   Added item: {cart_item.quantity} x {cart_item.menu_item.name}")
        
        print(f"   Total items added: {item_count}")

        # Clear the cart after successful order
        cart.items.all().delete()
        cart.restaurant = None
        cart.save()
        print("   Cart cleared")

        serializer = self.get_serializer(order)
        print(f"✅ Order created successfully: #{order.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Custom action to update order status"""
        try:
            order = self.get_object()
            new_status = request.data.get('status')
            
            print(f"📝 Updating order #{order.id} status from '{order.status}' to '{new_status}'")
            
            valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                return Response(
                    {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the status
            order.status = new_status
            order.save(update_fields=['status'])
            
            # Refresh to verify
            order.refresh_from_db()
            print(f"✅ Order #{order.id} status is now: {order.status}")
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
            
        except Exception as e:
            print(f"❌ Error updating order status: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )