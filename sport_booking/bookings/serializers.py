from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SportField, Booking
from datetime import datetime

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer สำหรับ User"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'role']
        read_only_fields = ['id', 'role']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        return user


class SportFieldSerializer(serializers.ModelSerializer):
    """Serializer สำหรับ SportField"""
    sport_type_display = serializers.CharField(source='get_sport_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SportField
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


