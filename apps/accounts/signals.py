"""
Signals for Accounts
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_default_role(sender, instance, created, **kwargs):
    """Assign default role to new users"""
    if created:
        from apps.rbac.models import Role, UserRole
        
        # Get default role
        default_role = Role.objects.filter(is_default=True, is_active=True).first()
        
        if default_role:
            UserRole.objects.create(
                user=instance,
                role=default_role,
                is_primary=True,
                is_active=True
            )
