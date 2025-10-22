from django.contrib import admin
from .models import BatteryStation, StationRental, StationReturn


@admin.register(BatteryStation)
class BatteryStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'business_hours', 'current_batteries', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'address', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'address', 'phone', 'description')
        }),
        ('地理位置', {
            'fields': ('latitude', 'longitude')
        }),
        ('运营信息', {
            'fields': ('business_hours', 'is_active')
        }),
        ('容量管理', {
            'fields': ('max_batteries', 'current_batteries')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StationRental)
class StationRentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'battery', 'station', 'rental_date', 'status', 'rental_amount')
    list_filter = ('status', 'rental_date', 'station')
    search_fields = ('user__username', 'battery__name', 'station__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('租赁信息', {
            'fields': ('station', 'user', 'battery')
        }),
        ('时间信息', {
            'fields': ('rental_date', 'expected_return_date', 'actual_return_date')
        }),
        ('费用信息', {
            'fields': ('rental_amount', 'status')
        }),
        ('备注', {
            'fields': ('notes',)
        }),
        ('系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StationReturn)
class StationReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'station', 'return_date', 'battery_condition', 'refund_amount')
    list_filter = ('battery_condition', 'return_date')
    search_fields = ('user__username', 'station__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('归还信息', {
            'fields': ('rental', 'station', 'user')
        }),
        ('归还详情', {
            'fields': ('return_date', 'battery_condition', 'notes')
        }),
        ('费用计算', {
            'fields': ('extra_fee', 'refund_amount')
        }),
        ('系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
