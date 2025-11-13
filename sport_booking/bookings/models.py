from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, time
from decimal import Decimal, ROUND_UP

class User(AbstractUser):
    """ขยาย Django User Model"""
    ROLE_CHOICES = [
        ('user', 'ผู้ใช้ทั่วไป'),
        ('admin', 'ผู้ดูแลระบบ'),
    ]
    
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    image = models.ImageField(upload_to='sport_fields/', blank=True, null=True, verbose_name='รูปภาพ')
    
    def __str__(self):
        return self.username


class SportField(models.Model):
    """สนามกีฬา"""
    SPORT_TYPES = [
        ('football', 'ฟุตบอล'),
        ('futsal', 'ฟุตซอล'),
        ('basketball', 'บาสเกตบอล'),
        ('volleyball', 'วอลเลย์บอล'),
        ('badminton', 'แบดมินตัน'),
        ('tennis', 'เทนนิส'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'พร้อมใช้งาน'),
        ('maintenance', 'ปิดปรับปรุง'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='ชื่อสนาม')
    sport_type = models.CharField(max_length=20, choices=SPORT_TYPES, verbose_name='ประเภทกีฬา')
    description = models.TextField(blank=True, verbose_name='รายละเอียด')
    capacity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='ความจุ (คน)')
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='ราคา/ชม.')
    image = models.ImageField(upload_to='sport_fields/', blank=True, null=True, verbose_name='รูปภาพ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='สถานะ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'สนามกีฬา'
        verbose_name_plural = 'สนามกีฬา'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_sport_type_display()})"


class Booking(models.Model):
    """การจองสนาม"""
    STATUS_CHOICES = [
        ('pending', 'รอยืนยัน'),
        ('confirmed', 'ยืนยันแล้ว'),
        ('cancelled', 'ยกเลิก'),
        ('completed', 'เสร็จสิ้น'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='ผู้จอง')
    sport_field = models.ForeignKey(SportField, on_delete=models.CASCADE, related_name='bookings', verbose_name='สนาม')
    booking_date = models.DateField(verbose_name='วันที่จอง')
    start_time = models.TimeField(verbose_name='เวลาเริ่มต้น')
    end_time = models.TimeField(verbose_name='เวลาสิ้นสุด')
    hours = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='จำนวนชั่วโมง')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคารวม')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    note = models.TextField(blank=True, verbose_name='หมายเหตุ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'การจอง'
        verbose_name_plural = 'การจอง'
        ordering = ['-booking_date', '-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.sport_field.name} ({self.booking_date})"
    
    def clean(self):
        """ตรวจสอบข้อมูลก่อนบันทึก"""
        # ตรวจสอบเวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด
        if self.start_time >= self.end_time:
            raise ValidationError('เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด')
        
        # ตรวจสอบว่าสนามถูกจองซ้ำหรือไม่
        overlapping_bookings = Booking.objects.filter(
            sport_field=self.sport_field,
            booking_date=self.booking_date,
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.pk)
        
        for booking in overlapping_bookings:
            # ตรวจสอบช่วงเวลาทับซ้อน
            if (self.start_time < booking.end_time and self.end_time > booking.start_time):
                raise ValidationError(f'สนามถูกจองในช่วงเวลานี้แล้ว ({booking.start_time} - {booking.end_time})')
    
    def save(self, *args, **kwargs):
    # คำนวณจำนวนชั่วโมงและราคารวม
        if self.start_time and self.end_time:
            start = datetime.combine(datetime.today(), self.start_time)
            end = datetime.combine(datetime.today(), self.end_time)
            duration = (end - start).total_seconds() / 3600
            self.hours = round(duration, 1)
    
            # คำนวณราคารวมและปัดเศษเป็น 2 ตำแหน่ง
            raw_total = Decimal(str(self.hours)) * self.sport_field.price_per_hour
            self.total_price = Decimal(round(float(raw_total), 2))
    
        try:
            self.full_clean()
            super().save(*args, **kwargs)
        except ValidationError as e:
            raise e