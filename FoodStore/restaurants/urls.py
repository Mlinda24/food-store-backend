from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, MenuItemViewSet, RestaurantMenuViewSet

router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='restaurant')
router.register('menu', MenuItemViewSet, basename='menu')
router.register('manage/menu', RestaurantMenuViewSet, basename='manage-menu')

urlpatterns = [
    path('', include(router.urls)),
]