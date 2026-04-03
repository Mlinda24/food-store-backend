from django.contrib import admin
from django.urls import path, include, re_path

# Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Food Store API",
        default_version='v1',
        description="API documentation for Food Store Backend",
        contact=openapi.Contact(email="your@email.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication APIs
    path('api/auth/', include('accounts.urls')),

    # Restaurant APIs
    path('api/', include('restaurants.urls')),

    # Orders APIs
    #path('api/orders/', include('orders.urls')),

    # DRF login/logout (for browsable API)
    path('api-auth/', include('rest_framework.urls')),

    # Swagger Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),

    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]