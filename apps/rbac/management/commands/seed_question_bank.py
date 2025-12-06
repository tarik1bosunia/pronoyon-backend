"""
Management command to seed Question Bank RBAC roles and permissions
Usage: python manage.py seed_question_bank
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import ProgrammingError, OperationalError
from apps.rbac.models import Permission, Role


class Command(BaseCommand):
    help = 'Seed RBAC roles and permissions for Question Bank application'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting Question Bank RBAC seeding...'))
            
            with transaction.atomic():
                # Create permissions
                self.create_permissions()
                
                # Create/Update roles for Question Bank
                self.create_roles()
                
                # Assign permissions to roles
                self.assign_permissions()
            
            self.stdout.write(self.style.SUCCESS('Question Bank RBAC seeding completed successfully!'))
        except (ProgrammingError, OperationalError) as e:
            self.stdout.write(
                self.style.WARNING(
                    f'Question Bank RBAC seeding skipped - database tables may not exist yet: {str(e)}'
                )
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during Question Bank RBAC seeding: {str(e)}')
            )
            raise
    
    def create_permissions(self):
        """Create all Question Bank permissions"""
        self.stdout.write('Creating Question Bank permissions...')
        
        permissions_data = [
            # Question Management (Managers)
            ('question.create', 'question-create', 'Create new questions', 'question'),
            ('question.view', 'question-view', 'View questions', 'question'),
            ('question.update', 'question-update', 'Update own questions', 'question'),
            ('question.delete', 'question-delete', 'Delete own questions', 'question'),
            ('question.verify', 'question-verify', 'Verify question quality', 'question'),
            ('question.bulk_create', 'question-bulk-create', 'Bulk create questions', 'question'),
            ('question.bulk_delete', 'question-bulk-delete', 'Bulk delete questions', 'question'),
            ('question.import', 'question-import', 'Import questions from file', 'question'),
            ('question.export', 'question-export', 'Export questions to file', 'question'),
            
            # Subject Management
            ('subject.create', 'subject-create', 'Create subjects', 'subject'),
            ('subject.view', 'subject-view', 'View subjects', 'subject'),
            ('subject.update', 'subject-update', 'Update subjects', 'subject'),
            ('subject.delete', 'subject-delete', 'Delete subjects', 'subject'),
            
            # Topic Management
            ('topic.create', 'topic-create', 'Create topics', 'topic'),
            ('topic.view', 'topic-view', 'View topics', 'topic'),
            ('topic.update', 'topic-update', 'Update topics', 'topic'),
            ('topic.delete', 'topic-delete', 'Delete topics', 'topic'),
            
            # Question Set Management
            ('questionset.create', 'questionset-create', 'Create question sets', 'question'),
            ('questionset.view', 'questionset-view', 'View question sets', 'question'),
            ('questionset.update', 'questionset-update', 'Update question sets', 'question'),
            ('questionset.delete', 'questionset-delete', 'Delete question sets', 'question'),
            ('questionset.generate', 'questionset-generate', 'Generate random question sets', 'question'),
            
            # Question Bank Management
            ('questionbank.create', 'questionbank-create', 'Create question banks', 'question'),
            ('questionbank.view', 'questionbank-view', 'View question banks', 'question'),
            ('questionbank.manage', 'questionbank-manage', 'Manage question banks', 'question'),
            
            # Draft Management (Users)
            ('draft.create', 'draft-create', 'Create personal drafts', 'draft'),
            ('draft.view', 'draft-view', 'View own drafts', 'draft'),
            ('draft.update', 'draft-update', 'Update own drafts', 'draft'),
            ('draft.delete', 'draft-delete', 'Delete own drafts', 'draft'),
            ('draft.add_question', 'draft-add-question', 'Add questions to draft', 'draft'),
            ('draft.remove_question', 'draft-remove-question', 'Remove questions from draft', 'draft'),
            ('draft.customize', 'draft-customize', 'Customize questions in draft', 'draft'),
            
            # PDF Export (Users with wallet balance)
            ('pdf.export', 'pdf-export', 'Export drafts to PDF (deducts from wallet)', 'pdf'),
            ('pdf.download', 'pdf-download', 'Download PDF files', 'pdf'),
            ('pdf.customize', 'pdf-customize', 'Customize PDF layout', 'pdf'),
            
            # Wallet Management (Users)
            ('wallet.view', 'wallet-view', 'View wallet balance', 'wallet'),
            ('wallet.topup', 'wallet-topup', 'Top up wallet via bKash', 'wallet'),
            ('wallet.history', 'wallet-history', 'View wallet transaction history', 'wallet'),
            ('wallet.view_all', 'wallet-view-all', 'View all user wallets (Admin)', 'wallet'),
            ('wallet.verify_topup', 'wallet-verify-topup', 'Verify bKash top-ups (Admin)', 'wallet'),
            
            # Payment Management (Admins)
            ('payment.view_all', 'payment-view-all', 'View all payments', 'payment'),
            ('payment.view_own', 'payment-view-own', 'View own payments', 'payment'),
            ('payment.verify', 'payment-verify', 'Verify bKash payments', 'payment'),
            ('payment.refund', 'payment-refund', 'Process refunds', 'payment'),
            ('payment.reports', 'payment-reports', 'Generate payment reports', 'payment'),
            
            # User Management (Admins) - Enhanced
            ('user.activate', 'user-activate', 'Activate users', 'user'),
            ('user.deactivate', 'user-deactivate', 'Deactivate users', 'user'),
            ('user.change_role', 'user-change-role', 'Change user roles', 'user'),
            ('user.view_activity', 'user-view-activity', 'View user activity logs', 'user'),
            
            # System/Admin
            ('system.view_logs', 'system-view-logs', 'View system logs', 'admin'),
            ('system.view_analytics', 'system-view-analytics', 'View system analytics', 'analytics'),
            ('system.manage_settings', 'system-manage-settings', 'Manage system settings', 'settings'),
        ]
        
        created_count = 0
        updated_count = 0
        
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
                created_count += 1
                self.stdout.write(f'  ✓ Created permission: {name}')
            else:
                # Update existing permission if needed
                updated = False
                if permission.description != description:
                    permission.description = description
                    updated = True
                if permission.category != category:
                    permission.category = category
                    updated = True
                if updated:
                    permission.save()
                    updated_count += 1
                    self.stdout.write(f'  ↻ Updated permission: {name}')
                else:
                    self.stdout.write(f'  - Permission exists: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Created {created_count} permissions, Updated {updated_count} permissions')
        )
    
    def create_roles(self):
        """Create/Update the 3 main roles for Question Bank"""
        self.stdout.write('Creating/Updating Question Bank roles...')
        
        roles_data = [
            # Three main roles for Question Bank
            ('Admin', 'admin', 'System administrator with user and payment management', 'system', 70, None, False),
            ('Manager', 'manager', 'Question manager responsible for building database', 'system', 60, None, False),
            ('User', 'user', 'Regular user who can view questions, create drafts, and export PDFs', 'system', 10, None, True),
        ]
        
        for name, slug, description, role_type, level, inherits_from_slug, is_default in roles_data:
            inherits_from = None
            if inherits_from_slug:
                inherits_from = Role.objects.filter(slug=inherits_from_slug).first()
            
            role, created = Role.objects.update_or_create(
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
                self.stdout.write(f'  ↻ Updated role: {name} (Level {level})')
    
    def assign_permissions(self):
        """Assign permissions to the 3 main roles"""
        self.stdout.write('Assigning permissions to roles...')
        
        # ADMIN ROLE (Level 70) - User management & Payment monitoring
        admin = Role.objects.get(slug='admin')
        admin_permissions = Permission.objects.filter(
            name__in=[
                # User Management
                'user.view', 'user.create', 'user.update', 'user.delete',
                'user.activate', 'user.deactivate', 'user.change_role',
                'user.view_activity', 'user.list',
                
                # Payment Monitoring
                'payment.view_all', 'payment.verify', 'payment.refund',
                'payment.reports',
                
                # Wallet Monitoring
                'wallet.view_all', 'wallet.verify_topup',
                
                # System
                'system.view_logs', 'system.view_analytics', 'system.manage_settings',
                
                # View access to questions (read-only)
                'question.view', 'subject.view', 'topic.view',
                'questionset.view', 'questionbank.view',
                
                # Admin panel access
                'admin.access', 'admin.users', 'admin.logs',
            ]
        )
        admin.permissions.set(admin_permissions)
        self.stdout.write(f'  ✓ Assigned {admin_permissions.count()} permissions to Admin')
        
        # MANAGER ROLE (Level 60) - Question database management
        manager = Role.objects.get(slug='manager')
        manager_permissions = Permission.objects.filter(
            name__in=[
                # Full question management
                'question.create', 'question.view', 'question.update',
                'question.delete', 'question.verify', 'question.bulk_create',
                'question.bulk_delete', 'question.import', 'question.export',
                
                # Subject management
                'subject.create', 'subject.view', 'subject.update', 'subject.delete',
                
                # Topic management
                'topic.create', 'topic.view', 'topic.update', 'topic.delete',
                
                # Question set management
                'questionset.create', 'questionset.view', 'questionset.update',
                'questionset.delete', 'questionset.generate',
                
                # Question bank management
                'questionbank.create', 'questionbank.view', 'questionbank.manage',
                
                # View own wallet and payment info
                'wallet.view', 'wallet.history',
                'payment.view_own',
            ]
        )
        manager.permissions.set(manager_permissions)
        self.stdout.write(f'  ✓ Assigned {manager_permissions.count()} permissions to Manager')
        
        # USER ROLE (Level 10) - Browse, draft, and export
        user = Role.objects.get(slug='user')
        user_permissions = Permission.objects.filter(
            name__in=[
                # View questions (FREE)
                'question.view', 'subject.view', 'topic.view',
                'questionset.view', 'questionbank.view',
                
                # Draft management (FREE)
                'draft.create', 'draft.view', 'draft.update', 'draft.delete',
                'draft.add_question', 'draft.remove_question', 'draft.customize',
                
                # PDF export (pay-per-print)
                'pdf.export', 'pdf.download', 'pdf.customize',
                
                # Wallet management
                'wallet.view', 'wallet.topup', 'wallet.history',
                
                # Payment (own)
                'payment.view_own',
            ]
        )
        user.permissions.set(user_permissions)
        self.stdout.write(f'  ✓ Assigned {user_permissions.count()} permissions to User')
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ All permissions assigned successfully!')
        )
