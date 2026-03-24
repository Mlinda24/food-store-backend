from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, MenuItemViewSet

router = DefaultRouter()
router.register('', RestaurantViewSet, basename='restaurant')
router.register('menu', MenuItemViewSet, basename='menu')

urlpatterns = [path('', include(router.urls))]