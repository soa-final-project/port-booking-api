from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SportField, Booking


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'phone_number']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ข้อมูลเพิ่มเติม', {'fields': ('phone_number', 'role')}),
    )


@admin.register(SportField)
class SportFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'sport_type', 'capacity', 'price_per_hour', 'status']
    list_filter = ['sport_type', 'status']
    search_fields = ['name', 'description']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'sport_field', 'booking_date', 'start_time', 'end_time', 'total_price', 'status']
    list_filter = ['status', 'booking_date', 'sport_field']
    search_fields = ['user__username', 'sport_field__name']
    date_hierarchy = 'booking_date'