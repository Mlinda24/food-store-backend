from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'phone']
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all fields for admin/restaurant views"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'first_name', 'last_name', 
                  'is_active', 'is_staff', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class PublicUserSerializer(serializers.ModelSerializer):
    """Public user serializer (limited info for public views)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'role']