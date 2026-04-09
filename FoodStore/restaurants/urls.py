from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantViewSet, MenuItemViewSet, AvailableMenuItemsViewSet
)

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('menu-items', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('menu/available/', AvailableMenuItemsViewSet.as_view({'get': 'list'}), name='available-menu'),
]