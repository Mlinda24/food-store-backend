from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum

from .models import Restaurant, MenuItem
from .serializers import RestaurantSerializer, MenuItemSerializer, MenuItemPublicSerializer

# ------------------------------
# Restaurant ViewSet
# ------------------------------
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get', 'patch'])
    def my_restaurant(self, request):
        try:
            restaurant = Restaurant.objects.get(owner=request.user)
            if request.method == 'GET':
                serializer = RestaurantSerializer(restaurant)
                return Response(serializer.data)
            elif request.method == 'PATCH':
                serializer = RestaurantSerializer(
                    restaurant, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Restaurant.DoesNotExist:
            return Response({'detail': 'No restaurant found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            restaurant = Restaurant.objects.get(owner=request.user)
            from orders.models import Order  # avoid circular import

            now = timezone.now()
            today = now.date()
            current_month = now.month
            current_year = now.year

            today_orders = Order.objects.filter(
                restaurant=restaurant, created_at__date=today
            )
            monthly_orders = Order.objects.filter(
                restaurant=restaurant,
                created_at__year=current_year,
                created_at__month=current_month
            )
            total_orders = Order.objects.filter(restaurant=restaurant)
            active_orders = Order.objects.filter(
                restaurant=restaurant, status__in=['pending','confirmed','preparing']
            )

            stats = {
                'today_earnings': today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0,
                'today_orders': today_orders.count(),
                'monthly_earnings': monthly_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0,
                'monthly_orders': monthly_orders.count(),
                'total_earnings': total_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0,
                'total_orders': total_orders.count(),
                'active_orders': active_orders.count(),
                'average_rating': 4.8,  # placeholder
            }
            return Response(stats)
        except Restaurant.DoesNotExist:
            return Response({'detail': 'No restaurant found'}, status=status.HTTP_404_NOT_FOUND)

# ------------------------------
# Menu Item ViewSets
# ------------------------------
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class RestaurantMenuViewSet(viewsets.ViewSet):
    def list(self, request, restaurant_pk=None):
        menu_items = MenuItem.objects.filter(restaurant_id=restaurant_pk)
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)

# ------------------------------
# New: All Available Menu Items
# ------------------------------
class AvailableMenuItemsViewSet(viewsets.ViewSet):
    """
    Returns all available menu items across all restaurants.
    """
    def list(self, request):
        menu_items = MenuItem.objects.filter(is_available=True, restaurant__is_open=True)
        serializer = MenuItemPublicSerializer(menu_items, many=True)
        return Response(serializer.data)