from django.contrib import admin
from django.utils.html import format_html
from .models import Permission, Role, UserRole, RoleHistory


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'codename', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'codename', 'category', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'role_type', 'level', 'user_count', 'is_active', 'is_default']
    list_filter = ['role_type', 'level', 'is_active', 'is_default']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at', 'user_count']
    filter_horizontal = ['permissions']
    ordering = ['-level', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Role Configuration', {
            'fields': ('role_type', 'level', 'inherits_from', 'max_users')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_default')
        }),
        ('Statistics', {
            'fields': ('user_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count(self, obj):
        count = obj.get_user_count()
        if obj.max_users:
            return format_html(
                '<span style="color: {};">{} / {}</span>',
                'red' if count >= obj.max_users else 'green',
                count,
                obj.max_users
            )
        return count
    user_count.short_description = 'User Count'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'is_primary', 'assigned_at', 'expires_at', 'is_expired_status']
    list_filter = ['role', 'is_active', 'is_primary', 'assigned_at']
    search_fields = ['user__email', 'role__name']
    readonly_fields = ['assigned_at', 'is_expired_status']
    autocomplete_fields = ['user', 'role', 'assigned_by']
    date_hierarchy = 'assigned_at'
    
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'role', 'assigned_by')
        }),
        ('Status', {
            'fields': ('is_active', 'is_primary', 'expires_at', 'is_expired_status')
        }),
        ('Context', {
            'fields': ('context', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('assigned_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired_status(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.expires_at:
            return format_html('<span style="color: orange;">Active (expires)</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_status.short_description = 'Status'


@admin.register(RoleHistory)
class RoleHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'action', 'performed_by', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email', 'role__name', 'reason']
    readonly_fields = ['user', 'role', 'action', 'performed_by', 'reason', 'metadata', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
