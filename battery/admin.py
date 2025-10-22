from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    BatteryCategory, BatteryType, Battery, BatteryUsage, 
    RentalOrder, BatteryReview, ReviewReply
)


@admin.register(BatteryCategory)
class BatteryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(BatteryType)
class BatteryTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'serial_number', 'battery_type', 'status', 
        'capacity', 'voltage', 'daily_rental_price', 'location', 'created_at'
    ]
    list_filter = ['status', 'battery_type__category', 'battery_type', 'created_at']
    search_fields = ['name', 'serial_number', 'location']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'serial_number', 'battery_type', 'status', 'image')
        }),
        ('技术参数', {
            'fields': ('capacity', 'voltage', 'power', 'weight')
        }),
        ('租赁信息', {
            'fields': ('daily_rental_price', 'deposit')
        }),
        ('位置信息', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('battery_type__category')


@admin.register(BatteryUsage)
class BatteryUsageAdmin(admin.ModelAdmin):
    list_display = [
        'battery', 'user', 'start_time', 'end_time', 
        'current_charge', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'start_time', 'created_at']
    search_fields = ['battery__name', 'user__username']
    ordering = ['-start_time']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('battery', 'user')


@admin.register(RentalOrder)
class RentalOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'battery', 'start_date', 
        'end_date', 'rental_days', 'total_amount', 'status', 'created_at'
    ]
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['order_number', 'user__username', 'battery__name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('订单信息', {
            'fields': ('order_number', 'user', 'battery', 'status')
        }),
        ('租赁详情', {
            'fields': ('start_date', 'end_date', 'rental_days')
        }),
        ('费用信息', {
            'fields': ('daily_price', 'total_amount', 'deposit_amount')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'battery')


@admin.register(BatteryReview)
class BatteryReviewAdmin(admin.ModelAdmin):
    list_display = [
        'battery', 'user', 'rating', 'comment_preview', 'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = ['battery__name', 'user__username', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def comment_preview(self, obj):
        if len(obj.comment) > 50:
            return obj.comment[:50] + '...'
        return obj.comment
    comment_preview.short_description = '评价内容'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('battery', 'user')


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = [
        'review', 'user', 'parent_reply', 'content_preview', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['user__username', 'content']
    ordering = ['created_at']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = '回复内容'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review', 'user', 'parent_reply')