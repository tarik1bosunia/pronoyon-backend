"""
Management command to seed RBAC roles and permissions
Usage: python manage.py seed_rbac
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import ProgrammingError, OperationalError
from apps.rbac.models import Permission, Role


class Command(BaseCommand):
    help = 'Seed RBAC roles and permissions for ReplyCompass'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting RBAC seeding...'))
            
            with transaction.atomic():
                # Create permissions
                self.create_permissions()
                
                # Create roles
                self.create_roles()
                
                # Assign permissions to roles
                self.assign_permissions()
            
            self.stdout.write(self.style.SUCCESS('RBAC seeding completed successfully!'))
        except (ProgrammingError, OperationalError) as e:
            self.stdout.write(
                self.style.WARNING(
                    f'RBAC seeding skipped - database tables may not exist yet: {str(e)}'
                )
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during RBAC seeding: {str(e)}')
            )
            raise
    
    def create_permissions(self):
        """Create all permissions"""
        self.stdout.write('Creating permissions...')
        
        permissions_data = [
            # User Management
            ('user.view', 'user-view', 'View users', 'user'),
            ('user.create', 'user-create', 'Create users', 'user'),
            ('user.update', 'user-update', 'Update users', 'user'),
            ('user.delete', 'user-delete', 'Delete users', 'user'),
            ('user.list', 'user-list', 'List all users', 'user'),
            ('user.export', 'user-export', 'Export user data', 'user'),
            ('user.impersonate', 'user-impersonate', 'Impersonate users', 'user'),
            
            # Content Management
            ('content.view', 'content-view', 'View content', 'content'),
            ('content.create', 'content-create', 'Create content', 'content'),
            ('content.update', 'content-update', 'Update content', 'content'),
            ('content.delete', 'content-delete', 'Delete content', 'content'),
            ('content.publish', 'content-publish', 'Publish content', 'content'),
            ('content.moderate', 'content-moderate', 'Moderate content', 'content'),
            
            # Analytics
            ('analytics.view', 'analytics-view', 'View analytics', 'analytics'),
            ('analytics.export', 'analytics-export', 'Export analytics', 'analytics'),
            ('analytics.dashboard', 'analytics-dashboard', 'Access analytics dashboard', 'analytics'),
            
            # Settings
            ('settings.view', 'settings-view', 'View settings', 'settings'),
            ('settings.update', 'settings-update', 'Update settings', 'settings'),
            ('settings.system', 'settings-system', 'Manage system settings', 'settings'),
            
            # Billing
            ('billing.view', 'billing-view', 'View billing information', 'billing'),
            ('billing.manage', 'billing-manage', 'Manage billing', 'billing'),
            ('billing.invoices', 'billing-invoices', 'Access invoices', 'billing'),
            
            # Support
            ('support.view', 'support-view', 'View support tickets', 'support'),
            ('support.respond', 'support-respond', 'Respond to support tickets', 'support'),
            ('support.manage', 'support-manage', 'Manage support system', 'support'),
            
            # API Access
            ('api.read', 'api-read', 'Read API access', 'api'),
            ('api.write', 'api-write', 'Write API access', 'api'),
            ('api.admin', 'api-admin', 'Admin API access', 'api'),
            
            # Administration
            ('admin.access', 'admin-access', 'Access admin panel', 'admin'),
            ('admin.users', 'admin-users', 'Manage users in admin', 'admin'),
            ('admin.roles', 'admin-roles', 'Manage roles and permissions', 'admin'),
            ('admin.logs', 'admin-logs', 'View system logs', 'admin'),
            ('admin.system', 'admin-system', 'System administration', 'admin'),
        ]
        
        for name, codename, description, category in permissions_data:
            permission, created = Permission.objects.get_or_create(
                name=name,
                defaults={
                    'codename': codename,
                    'description': description,
                    'category': category,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created permission: {name}')
            else:
                self.stdout.write(f'  - Permission exists: {name}')
    
    def create_roles(self):
        """Create all roles"""
        self.stdout.write('Creating roles...')
        
        roles_data = [
            # Basic roles
            ('Guest', 'guest', 'Guest user with limited access', 'system', 0, None, False),
            ('User', 'user', 'Standard user', 'system', 10, None, True),
            ('Premium User', 'premium-user', 'Premium subscription user', 'system', 20, 'user', False),
            
            # Moderation roles
            ('Moderator', 'moderator', 'Content moderator', 'system', 30, 'user', False),
            ('Content Manager', 'content-manager', 'Manages content and moderators', 'system', 40, 'moderator', False),
            
            # Support roles
            ('Support Agent', 'support-agent', 'Customer support agent', 'system', 50, 'user', False),
            
            # Management roles
            ('Manager', 'manager', 'Team manager', 'system', 60, 'content-manager', False),
            ('Admin', 'admin', 'Administrator', 'system', 70, 'manager', False),
            ('Super Admin', 'super-admin', 'Super administrator with full access', 'system', 80, 'admin', False),
        ]
        
        for name, slug, description, role_type, level, inherits_from_slug, is_default in roles_data:
            inherits_from = None
            if inherits_from_slug:
                inherits_from = Role.objects.filter(slug=inherits_from_slug).first()
            
            role, created = Role.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'role_type': role_type,
                    'level': level,
                    'inherits_from': inherits_from,
                    'is_default': is_default,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created role: {name} (Level {level})')
            else:
                self.stdout.write(f'  - Role exists: {name}')
    
    def assign_permissions(self):
        """Assign permissions to roles"""
        self.stdout.write('Assigning permissions to roles...')
        
        # Guest - minimal access
        guest = Role.objects.get(slug='guest')
        guest.permissions.set([
            Permission.objects.get(name='content.view'),
        ])
        self.stdout.write(f'  ✓ Assigned {guest.permissions.count()} permissions to Guest')
        
        # User - basic access
        user = Role.objects.get(slug='user')
        user.permissions.set([
            Permission.objects.get(name='content.view'),
            Permission.objects.get(name='content.create'),
            Permission.objects.get(name='user.view'),
            Permission.objects.get(name='settings.view'),
            Permission.objects.get(name='api.read'),
        ])
        self.stdout.write(f'  ✓ Assigned {user.permissions.count()} permissions to User')
        
        # Premium User - inherits from User + additional features
        premium = Role.objects.get(slug='premium-user')
        premium.permissions.set([
            Permission.objects.get(name='analytics.view'),
            Permission.objects.get(name='analytics.dashboard'),
            Permission.objects.get(name='api.write'),
        ])
        self.stdout.write(f'  ✓ Assigned {premium.permissions.count()} permissions to Premium User')
        
        # Moderator - content moderation
        moderator = Role.objects.get(slug='moderator')
        moderator.permissions.set([
            Permission.objects.get(name='content.moderate'),
            Permission.objects.get(name='content.update'),
            Permission.objects.get(name='content.delete'),
            Permission.objects.get(name='user.list'),
        ])
        self.stdout.write(f'  ✓ Assigned {moderator.permissions.count()} permissions to Moderator')
        
        # Content Manager - manages content and moderators
        content_manager = Role.objects.get(slug='content-manager')
        content_manager.permissions.set([
            Permission.objects.get(name='content.publish'),
            Permission.objects.get(name='analytics.view'),
            Permission.objects.get(name='user.update'),
        ])
        self.stdout.write(f'  ✓ Assigned {content_manager.permissions.count()} permissions to Content Manager')
        
        # Support Agent - customer support
        support = Role.objects.get(slug='support-agent')
        support.permissions.set([
            Permission.objects.get(name='support.view'),
            Permission.objects.get(name='support.respond'),
            Permission.objects.get(name='user.view'),
            Permission.objects.get(name='user.list'),
        ])
        self.stdout.write(f'  ✓ Assigned {support.permissions.count()} permissions to Support Agent')
        
        # Manager - team management
        manager = Role.objects.get(slug='manager')
        manager.permissions.set([
            Permission.objects.get(name='user.create'),
            Permission.objects.get(name='user.export'),
            Permission.objects.get(name='analytics.export'),
            Permission.objects.get(name='support.manage'),
            Permission.objects.get(name='billing.view'),
        ])
        self.stdout.write(f'  ✓ Assigned {manager.permissions.count()} permissions to Manager')
        
        # Admin - administration
        admin = Role.objects.get(slug='admin')
        admin.permissions.set([
            Permission.objects.get(name='user.delete'),
            Permission.objects.get(name='settings.update'),
            Permission.objects.get(name='billing.manage'),
            Permission.objects.get(name='admin.access'),
            Permission.objects.get(name='admin.users'),
            Permission.objects.get(name='admin.logs'),
            Permission.objects.get(name='api.admin'),
        ])
        self.stdout.write(f'  ✓ Assigned {admin.permissions.count()} permissions to Admin')
        
        # Super Admin - full access
        super_admin = Role.objects.get(slug='super-admin')
        super_admin.permissions.set([
            Permission.objects.get(name='user.impersonate'),
            Permission.objects.get(name='settings.system'),
            Permission.objects.get(name='admin.roles'),
            Permission.objects.get(name='admin.system'),
            Permission.objects.get(name='billing.invoices'),
        ])
        self.stdout.write(f'  ✓ Assigned {super_admin.permissions.count()} permissions to Super Admin')
