from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'primary_role_display', 'is_active', 'is_verified', 'date_joined']
    list_filter = ['is_active', 'is_verified', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'primary_role_display', 'all_roles_display']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'bio')
        }),
        ('Roles & Permissions', {
            'fields': ('primary_role_display', 'all_roles_display', 'is_staff', 'is_superuser')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name')
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff')
        }),
    )
    
    def primary_role_display(self, obj):
        role = obj.get_primary_role()
        if role:
            return format_html(
                '<span style="background: #417690; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                role.name
            )
        return format_html('<span style="color: #999;">No role</span>')
    primary_role_display.short_description = 'Primary Role'
    
    def all_roles_display(self, obj):
        roles = obj.get_active_roles()
        if roles:
            role_badges = []
            for user_role in roles:
                badge_html = format_html(
                    '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 3px; margin-right: 5px;">{}</span>',
                    '#28a745' if user_role.is_primary else '#6c757d',
                    user_role.role.name
                )
                role_badges.append(badge_html)
            return format_html(''.join(str(badge) for badge in role_badges))
        return format_html('<span style="color: #999;">No roles</span>')
    all_roles_display.short_description = 'All Roles'
