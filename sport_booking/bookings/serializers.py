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


class BookingSerializer(serializers.ModelSerializer):
    """Serializer สำหรับ Booking"""
    user_detail = UserSerializer(source='user', read_only=True)
    sport_field_detail = SportFieldSerializer(source='sport_field', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'user', 'hours', 'total_price', 'created_at', 'updated_at']
    
    def validate(self, data):
        """ตรวจสอบข้อมูลเพิ่มเติม"""
        # ตรวจสอบว่าวันที่จองไม่ใช่วันที่ผ่านมาแล้ว
        if data.get('booking_date'):
            if data['booking_date'] < datetime.now().date():
                raise serializers.ValidationError({'booking_date': 'ไม่สามารถจองย้อนหลังได้'})
        
        # ตรวจสอบสถานะสนาม
        sport_field = data.get('sport_field')
        if sport_field and sport_field.status != 'available':
            raise serializers.ValidationError({'sport_field': 'สนามนี้ไม่พร้อมให้บริการในขณะนี้'})
        
        return data
    
    def create(self, validated_data):
        # กำหนด user จาก request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer สำหรับสร้างการจอง (แบบง่าย)"""
    
    class Meta:
        model = Booking
        fields = ['sport_field', 'booking_date', 'start_time', 'end_time', 'note']
    
    def validate(self, data):
        """ตรวจสอบข้อมูล"""
        if data['booking_date'] < datetime.now().date():
            raise serializers.ValidationError({'booking_date': 'ไม่สามารถจองย้อนหลังได้'})
        
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({'end_time': 'เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น'})
        
        sport_field = data['sport_field']
        if sport_field.status != 'available':
            raise serializers.ValidationError({'sport_field': 'สนามนี้ไม่พร้อมให้บริการ'})
        
        return data