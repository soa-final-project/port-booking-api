from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import render  
from .models import SportField, Booking
from .serializers import (
    UserSerializer, 
    SportFieldSerializer, 
    BookingSerializer,
    BookingCreateSerializer
)
from datetime import datetime, timedelta

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """Permission สำหรับ Admin เท่านั้น"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet สำหรับจัดการ User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """ดูข้อมูลตัวเอง"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class SportFieldViewSet(viewsets.ModelViewSet):
    """ViewSet สำหรับจัดการสนามกีฬา"""
    queryset = SportField.objects.all()
    serializer_class = SportFieldSerializer
    
    def get_permissions(self):
        # อนุญาตให้ทุกคนเข้าถึง list, retrieve, availability โดยไม่ต้องล็อกอิน
        if self.action in ['list', 'retrieve', 'availability']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """ตรวจสอบช่วงเวลาว่างของสนาม"""
        sport_field = self.get_object()
        date_str = request.query_params.get('date', datetime.now().date())
        
        try:
            if isinstance(date_str, str):
                booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                booking_date = date_str
        except ValueError:
            return Response(
                {'error': 'รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ดึงการจองทั้งหมดในวันนั้น
        bookings = Booking.objects.filter(
            sport_field=sport_field,
            booking_date=booking_date,
            status__in=['pending', 'confirmed']
        ).order_by('start_time')
        
        booked_slots = [
            {
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
            }
            for booking in bookings
        ]
        
        return Response({
            'sport_field': sport_field.name,
            'date': booking_date,
            'booked_slots': booked_slots,
            'status': sport_field.status
        })


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet สำหรับจัดการการจอง"""
    queryset = Booking.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        """แสดงเฉพาะการจองของตัวเอง (ยกเว้น Admin)"""
        if self.request.user.role == 'admin':
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """บันทึกการจองพร้อมกำหนด user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """ดูการจองของตัวเอง"""
        bookings = Booking.objects.filter(user=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """ยกเลิกการจอง"""
        booking = self.get_object()
        
        # ตรวจสอบว่าเป็นเจ้าของการจองหรือ Admin
        if booking.user != request.user and request.user.role != 'admin':
            return Response(
                {'error': 'คุณไม่มีสิทธิ์ยกเลิกการจองนี้'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # ตรวจสอบว่าสามารถยกเลิกได้หรือไม่
        if booking.status in ['cancelled', 'completed']:
            return Response(
                {'error': f'ไม่สามารถยกเลิกการจองที่มีสถานะ {booking.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """ยืนยันการจอง (Admin เท่านั้น)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'เฉพาะ Admin เท่านั้นที่สามารถยืนยันการจองได้'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking = self.get_object()
        
        if booking.status != 'pending':
            return Response(
                {'error': 'สามารถยืนยันได้เฉพาะการจองที่รอยืนยันเท่านั้น'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)