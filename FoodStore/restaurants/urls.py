from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantViewSet, 
    MenuItemViewSet, 
    AvailableMenuItemsViewSet,
    RestaurantMenuViewSet
)

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('menu/available/', AvailableMenuItemsViewSet.as_view({'get': 'list'}), name='available-menu'),
    path('restaurants/<int:restaurant_pk>/menu/', RestaurantMenuViewSet.as_view({'get': 'list'}), name='restaurant-menu'),
]