from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import (
    CustomUser, UserProfile, UserPreference, UserPoints, 
    UserMessage, UserLoginLog, UserFavorite
)


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # 显示字段
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'head_thumbnail', 'describe_preview', 'is_staff', 'is_active', 'date_joined'
    ]
    
    # 过滤器
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'date_joined']
    
    # 搜索字段
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # 排序
    ordering = ['-date_joined']
    
    # 只读字段
    readonly_fields = ['date_joined', 'last_login']
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email', 'password')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'head', 'describe')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('时间信息', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # 添加用户时的字段分组
    add_fieldsets = (
        ('基本信息', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'head', 'describe')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    def head_thumbnail(self, obj):
        """显示头像缩略图"""
        if obj.head:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%;" />',
                obj.head.url
            )
        return format_html(
            '<img src="/static/img/default_avatar.png" width="40" height="40" style="border-radius: 50%;" />'
        )
    head_thumbnail.short_description = '头像'
    
    def describe_preview(self, obj):
        """显示个人描述预览"""
        if obj.describe:
            if len(obj.describe) > 30:
                return obj.describe[:30] + '...'
            return obj.describe
        return '-'
    describe_preview.short_description = '个人描述'


# 内联管理类
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'


class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = '用户偏好'


# 重新注册CustomUser，添加内联
admin.site.unregister(CustomUser)
@admin.register(CustomUser)
class CustomUserAdminWithInline(BaseUserAdmin):
    inlines = (UserProfileInline, UserPreferenceInline)
    
    # 显示字段
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'head_thumbnail', 'describe_preview', 'phone', 'balance', 
        'credit_score', 'is_verified', 'is_staff', 'is_active', 'created_at'
    ]
    
    # 过滤器
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'is_verified', 'created_at']
    
    # 搜索字段
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    
    # 排序
    ordering = ['-created_at']
    
    # 只读字段
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email', 'password')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'head', 'describe', 'phone')
        }),
        ('账户信息', {
            'fields': ('balance', 'credit_score', 'is_verified')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('时间信息', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 添加用户时的字段分组
    add_fieldsets = (
        ('基本信息', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'head', 'describe', 'phone')
        }),
        ('账户信息', {
            'fields': ('balance', 'credit_score', 'is_verified')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )
    
    def head_thumbnail(self, obj):
        """显示头像缩略图"""
        if obj.head:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%;" />',
                obj.head.url
            )
        return format_html(
            '<img src="/static/img/default_avatar.png" width="40" height="40" style="border-radius: 50%;" />'
        )
    head_thumbnail.short_description = '头像'
    
    def describe_preview(self, obj):
        """显示个人描述预览"""
        if obj.describe:
            if len(obj.describe) > 30:
                return obj.describe[:30] + '...'
            return obj.describe
        return '-'
    describe_preview.short_description = '个人描述'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'birthday', 'occupation', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__username', 'occupation', 'company']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'theme', 'email_notifications', 'sms_notifications', 'auto_renewal']
    list_filter = ['language', 'theme', 'email_notifications', 'sms_notifications', 'auto_renewal']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'point_type', 'reason', 'balance_after', 'created_at']
    list_filter = ['point_type', 'created_at']
    search_fields = ['user__username', 'reason', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_type', 'title', 'is_read', 'is_important', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_important', 'created_at']
    search_fields = ['user__username', 'title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'read_at']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "标记为已读"
    
    actions = [mark_as_read]


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_time', 'logout_time', 'is_successful']
    list_filter = ['is_successful', 'login_time']
    search_fields = ['user__username', 'ip_address', 'failure_reason']
    ordering = ['-login_time']
    readonly_fields = ['login_time', 'logout_time']


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'battery_name', 'battery_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'battery_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']